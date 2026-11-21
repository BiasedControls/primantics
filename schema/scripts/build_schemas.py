# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
"""Discover and build every USD schema plugin under ``source/extensions/``.

Each schema is built as its own CMake project (its own configure / build /
install cycle) so per-schema ``CMAKE_INSTALL_PREFIX`` values don't collide
under a shared install root. See ``schema/CMakeLists.txt`` for the harness
each invocation uses.

Discovery: any folder containing a ``schema.usda`` file AND a sibling
``CMakeLists.txt`` is treated as a schema plugin. The schema library name
comes from the ``libraryName`` attribute inside ``schema.usda`` (falling
back to the plugin folder name).

Schemas are built in parallel (one worker per schema by default). A single
persistent venv with jinja2 (required by usdGenSchema) is created once under
``_build/schemagen_venv`` and shared by every schema build. Output of each
parallel build goes to ``_build/cmake/<schema>/build.log``.
"""

from __future__ import annotations

import os
import re
import sys
import time
import shutil
import argparse
import subprocess
from typing import TextIO
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed


_LIBRARY_NAME_RE = re.compile(r'libraryName\s*=\s*"([^"]+)"')
_JINJA2_VERSION = "3.1.4"


def _repo_root() -> Path:
    """``<repo>/schema/scripts/build_schemas.py`` -> ``<repo>``."""
    return Path(__file__).resolve().parents[2]


def _discover_schemas(source_root: Path) -> list[tuple[str, Path]]:
    """Return ``[(schema_name, plugin_dir), ...]`` for each valid schema.

    Any ``schema.usda`` without a sibling ``CMakeLists.txt`` is skipped with
    a warning so scratch/experimental usda files don't fail the build.
    """
    schemas: list[tuple[str, Path]] = []

    for usda in sorted(source_root.rglob("schema.usda")):
        plugin_dir = usda.parent
        if not (plugin_dir / "CMakeLists.txt").exists():
            print(
                f"[build_schemas] Skipping {plugin_dir}: found schema.usda " f"but no sibling CMakeLists.txt.",
                file=sys.stderr,
            )
            continue
        try:
            text = usda.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"[build_schemas] Could not read {usda}: {exc}", file=sys.stderr)
            continue
        match = _LIBRARY_NAME_RE.search(text)
        name = match.group(1) if match else plugin_dir.name
        schemas.append((name, plugin_dir))
    return schemas


def _select_schemas(schemas: list[tuple[str, Path]], schema_name: str) -> list[tuple[str, Path]]:
    """Return schemas whose library name matches ``schema_name``.

    ``all`` (any case) keeps every discovered schema.
    """
    if schema_name.lower() == "all":
        return schemas
    wanted = schema_name.lower()
    return [(name, plugin_dir) for name, plugin_dir in schemas if name.lower() == wanted]


def _print_schemas(schemas: list[tuple[str, Path]]) -> None:
    """Print discovered schemas as ``name: plugin_dir`` lines."""
    if not schemas:
        print("[build_schemas] No schemas found.")
        return
    print(f"[build_schemas] Found {len(schemas)} schema(s):")
    for name, plugin_dir in schemas:
        print(f"  {name}: {plugin_dir}")


def _run(cmd: list[str], label: str, log: TextIO | None = None) -> int:
    """Print and run ``cmd``; return its exit code.

    When ``log`` is given, the header and all process output go to it instead
    of the console.
    """
    header = f"[build_schemas] === {label} ===\n[build_schemas] $ {' '.join(cmd)}\n"
    if log is None:
        print(header, end="", flush=True)
        return subprocess.call(cmd)
    log.write(header)
    log.flush()
    return subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT)


# --- Shared schemagen venv ---


def _usd_python(repo_root: Path) -> Path:
    """Python that OpenUSD is built against (matches ``schema/PackmanDeps.cmake``)."""
    python_dir = repo_root / "_build" / "target-deps" / "python"
    if os.name == "nt":
        return python_dir / "python.exe"
    return python_dir / "bin" / "python3"


def _venv_python(venv_dir: Path) -> Path:
    """Python executable inside ``venv_dir``."""
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _venv_is_ready(venv_dir: Path) -> bool:
    """True if ``venv_dir`` exists and has the pinned jinja2 installed."""
    venv_python = _venv_python(venv_dir)
    if not venv_python.exists():
        return False
    check = subprocess.run(
        [str(venv_python), "-c", f"import sys, jinja2; sys.exit(jinja2.__version__ != '{_JINJA2_VERSION}')"],
        capture_output=True,
    )
    return check.returncode == 0


def _ensure_schemagen_venv(base_python: Path, venv_dir: Path) -> bool:
    """Create (or reuse) the venv shared by every schema's usdGenSchema step.

    ``NvPxrPlugin.cmake`` reuses the venv at this same path. Creating it here,
    before the parallel builds start, keeps concurrent configures from racing
    to create it.

    Returns False if the venv could not be created.
    """
    if _venv_is_ready(venv_dir):
        print(f"[build_schemas] Reusing schemagen venv at {venv_dir}")
        return True

    if not base_python.exists():
        print(
            f"[build_schemas] OpenUSD Python not found at {base_python}. " f"Build the repo first.",
            file=sys.stderr,
        )
        return False

    if venv_dir.exists():
        print(f"[build_schemas] Recreating stale schemagen venv at {venv_dir}")
        shutil.rmtree(venv_dir, ignore_errors=True)

    rc = _run([str(base_python), "-m", "venv", str(venv_dir)], "Creating schemagen venv")
    if rc != 0:
        return False
    pip_cmd = [str(_venv_python(venv_dir)), "-m", "pip", "install", f"jinja2=={_JINJA2_VERSION}"]
    rc = _run(pip_cmd, "Installing jinja2 into schemagen venv")
    return rc == 0


# --- Schema builds ---


def _build_one(
    schema_name: str,
    plugin_dir: Path,
    schema_project_dir: Path,
    build_dir: Path,
    install_dir: Path,
    config: str,
    log: TextIO | None = None,
) -> tuple[int, dict[str, float]]:
    """Configure, build, and install a single schema.

    Returns ``(exit_code, step_seconds)``: the first non-zero exit code
    encountered (or 0 on success), and the elapsed time of each step that ran.
    """
    timings: dict[str, float] = {}

    def run_step(step: str, cmd: list[str], label: str) -> int:
        start = time.monotonic()
        rc = _run(cmd, label, log)
        timings[step] = time.monotonic() - start
        return rc

    configure_cmd = [
        "cmake",
        "-S",
        str(schema_project_dir),
        "-B",
        str(build_dir),
        f"-DCMAKE_INSTALL_PREFIX={install_dir}",
        f"-DSCHEMA_PLUGIN_DIR={plugin_dir}",
    ]
    rc = run_step("configure", configure_cmd, f"Configuring '{schema_name}'")
    if rc != 0:
        return rc, timings

    build_cmd = [
        "cmake",
        "--build",
        str(build_dir),
        "--config",
        config,
    ]
    rc = run_step("build", build_cmd, f"Building '{schema_name}'")
    if rc != 0:
        return rc, timings

    install_cmd = [
        "cmake",
        "--install",
        str(build_dir),
        "--config",
        config,
    ]
    rc = run_step("install", install_cmd, f"Installing '{schema_name}' -> {install_dir}")
    return rc, timings


def _format_timings(timings: dict[str, float]) -> str:
    """Format step timings as ``total (configure 1.0s, build 2.0s, ...)``."""
    total = sum(timings.values())
    steps = ", ".join(f"{step} {seconds:.1f}s" for step, seconds in timings.items())
    return f"{total:.1f}s ({steps})"


def _build_one_logged(schema_name: str, build_dir: Path, **kwargs) -> tuple[int, Path, dict[str, float]]:
    """Run ``_build_one`` with output captured to ``<build_dir>/build.log``.

    Returns ``(exit_code, log_path, step_seconds)``.
    """
    build_dir.mkdir(parents=True, exist_ok=True)
    log_path = build_dir / "build.log"
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        rc, timings = _build_one(schema_name=schema_name, build_dir=build_dir, log=log, **kwargs)
    return rc, log_path, timings


def _build_all(
    selected: list[tuple[str, Path]],
    jobs: int,
    schema_project_dir: Path,
    build_root: Path,
    install_root: Path,
    config: str,
) -> list[str]:
    """Build every selected schema using up to ``jobs`` parallel workers.

    Returns the names of schemas that failed.
    """
    failed: list[str] = []

    if jobs == 1:
        for schema_name, plugin_dir in selected:
            rc, timings = _build_one(
                schema_name=schema_name,
                plugin_dir=plugin_dir,
                schema_project_dir=schema_project_dir,
                build_dir=build_root / schema_name,
                install_dir=install_root / schema_name,
                config=config,
            )
            if rc == 0:
                print(f"[build_schemas] '{schema_name}' succeeded in {_format_timings(timings)}", flush=True)
                continue
            print(
                f"[build_schemas] '{schema_name}' FAILED (exit code {rc}) after {_format_timings(timings)}.",
                file=sys.stderr,
            )
            failed.append(schema_name)
        return failed

    print(f"[build_schemas] Building with {jobs} parallel worker(s)...", flush=True)
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = {
            pool.submit(
                _build_one_logged,
                schema_name=schema_name,
                build_dir=build_root / schema_name,
                plugin_dir=plugin_dir,
                schema_project_dir=schema_project_dir,
                install_dir=install_root / schema_name,
                config=config,
            ): schema_name
            for schema_name, plugin_dir in selected
        }
        for future in as_completed(futures):
            schema_name = futures[future]
            rc, log_path, timings = future.result()
            if rc == 0:
                print(
                    f"[build_schemas] '{schema_name}' succeeded in {_format_timings(timings)} (log: {log_path})",
                    flush=True,
                )
                continue
            failed.append(schema_name)
            print(
                f"[build_schemas] '{schema_name}' FAILED (exit code {rc}) after {_format_timings(timings)}. "
                f"Log ({log_path}):",
                file=sys.stderr,
            )
            print(log_path.read_text(encoding="utf-8", errors="replace"), file=sys.stderr, flush=True)
    return failed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--config",
        default="Release",
        help="CMake config to build (Release, Debug, RelWithDebInfo).",
    )
    parser.add_argument(
        "--schema",
        default="all",
        help="Schema libraryName to build, or 'all' (default).",
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Print matching schemas and exit without building.",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=0,
        help="Max schemas to build in parallel (default 0: all at once; 1: sequential with live output).",
    )
    args = parser.parse_args()

    repo_root = _repo_root()
    schema_project_dir = repo_root / "schema"
    build_root = repo_root / "_build" / "cmake"
    install_root = repo_root / "_install"
    venv_dir = repo_root / "_build" / "schemagen_venv"
    source_ext = repo_root / "source" / "extensions"

    if not source_ext.exists():
        print(
            f"[build_schemas] No source/extensions/ directory at {source_ext}; " f"nothing to build.",
            file=sys.stderr,
        )
        return 1

    schemas = _discover_schemas(source_ext)
    selected = _select_schemas(schemas, args.schema)
    if not selected:
        if args.schema.lower() == "all":
            print(
                "[build_schemas] No schema.usda files found under " f"{source_ext}. Nothing to build.",
                file=sys.stderr,
            )
        else:
            available = ", ".join(name for name, _ in schemas) or "(none)"
            print(
                f"[build_schemas] Unknown schema '{args.schema}'. " f"Available: {available}",
                file=sys.stderr,
            )
        return 1

    if args.discover:
        _print_schemas(selected)
        return 0

    schema_names = ", ".join(name for name, _ in selected)
    print(f"[build_schemas] Discovered {len(selected)} schema(s): {schema_names}")

    venv_start = time.monotonic()
    if not _ensure_schemagen_venv(_usd_python(repo_root), venv_dir):
        print("[build_schemas] Failed to set up the schemagen venv. Aborting.", file=sys.stderr)
        return 1
    print(f"[build_schemas] Schemagen venv ready in {time.monotonic() - venv_start:.1f}s")

    jobs = args.jobs if args.jobs > 0 else len(selected)
    jobs = min(jobs, len(selected))
    start = time.monotonic()
    failed = _build_all(
        selected=selected,
        jobs=jobs,
        schema_project_dir=schema_project_dir,
        build_root=build_root,
        install_root=install_root,
        config=args.config,
    )
    elapsed = time.monotonic() - start

    if failed:
        print(
            f"[build_schemas] {len(failed)} of {len(selected)} schema(s) failed: {', '.join(failed)}",
            file=sys.stderr,
        )
        return 1

    print(f"[build_schemas] All {len(selected)} schema(s) built successfully in {elapsed:.1f}s.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
