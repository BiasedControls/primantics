# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
"""Stubgen wrapper for USD schema extensions.

Called from ``repo.toml`` ``post_build.commands``. Given one or more
``--ext <extension_name>`` arguments, this script launches Kit **once** with
every schema extension enabled and issues one ``pybind11_stubgen`` ``--exec``
per extension, so each schema's generated ``.pyd`` gets stubbed in a single
Kit boot.

Why not use ``repo stubgen`` directly?
    Standard ``repo stubgen`` misses USD schema ``.pyd`` files because they
    don't carry the ``*cp*.pyd`` ABI tag pybind11's default stubber looks
    for. Schemas also need to be imported under a real Kit launch so that
    dependencies like ``omni.usd.libs`` resolve, which is why we bootstrap
    kit and enable the extensions here.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    """Return the repository root (``<repo>/tools/repoman/`` -> ``<repo>``)."""
    return Path(__file__).resolve().parents[2]


def _forward_slashes(p: Path) -> str:
    """Kit accepts both slash styles but forward slashes avoid backslash
    escaping quirks when the path lands inside a quoted ``--exec`` string."""
    return str(p).replace("\\", "/")


def _build_command(
    kit_exe: Path,
    app: str,
    ext_names: list[str],
    ext_folder: Path,
    extscache_folder: Path,
    portable_root: Path,
) -> tuple[list[str], list[str]]:
    """Compose the Kit launcher command and return ``(cmd, stubbed_exts)``.

    ``stubbed_exts`` lists only the extensions whose build directory exists
    on disk; any missing extension is warned about and skipped from the
    ``--exec`` list, but still enabled (so a partial build still stubs what
    it can).
    """
    cmd: list[str] = [
        str(kit_exe),
        app,
        "--disable-ext-startup",
        "--allow-root",
    ]

    # Enable every schema in one launch so Kit only bootstraps once.
    for ext in ext_names:
        cmd += ["--enable", ext]

    # One --exec per schema so each stub lands next to its own extension.
    stubbed: list[str] = []
    for ext in ext_names:
        ext_build_dir = ext_folder / ext
        if not ext_build_dir.exists():
            print(
                f"[stubgen_schemas] Warning: {ext_build_dir} not found; "
                f"skipping stubgen for '{ext}'",
                file=sys.stderr,
            )
            continue
        cmd += [
            "--exec",
            (
                f'pybind11_stubgen.py -i "{_forward_slashes(ext_build_dir)}" '
                f'-e "{_forward_slashes(extscache_folder)}"'
            ),
        ]
        stubbed.append(ext)

    cmd += [
        "--portable-root", _forward_slashes(portable_root),
        "--ext-folder", _forward_slashes(ext_folder),
        "--ext-folder", _forward_slashes(extscache_folder),
        "--/app/python/logSysStdOutput=false",
        "--/app/enableStdoutOutput=0",
        "--/plugins/carb.scripting-python.plugin/logScriptErrors=true",
        "--/log/flushStandardStreamOutput=1",
        "--/app/extensions/fastImporter/enabled=0",
        "--/app/extensions/mkdirExtFolders=0",
    ]

    return cmd, stubbed


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--config", required=True, help="release|debug|relwithdebinfo")
    parser.add_argument(
        "--platform", required=True, help="e.g. windows-x86_64, linux-x86_64"
    )
    parser.add_argument(
        "--app",
        required=True,
        help="Path to the .kit app used to bootstrap the Kit runtime.",
    )
    parser.add_argument(
        "--ext",
        action="append",
        default=[],
        metavar="EXT_NAME",
        help=(
            "Name of a schema extension (as it appears in extension.toml) to "
            "stub. Pass this flag once per schema."
        ),
    )
    args = parser.parse_args()

    if not args.ext:
        print("[stubgen_schemas] No --ext given; nothing to stub.")
        return 0

    repo_root = _repo_root()
    build_root = repo_root / "_build" / args.platform / args.config
    kit_exe_name = "kit.exe" if args.platform.startswith("windows") else "kit"
    kit_exe = build_root / "kit" / kit_exe_name
    if not kit_exe.exists():
        print(
            f"[stubgen_schemas] Kit executable not found: {kit_exe}",
            file=sys.stderr,
        )
        return 1

    ext_folder = build_root / "exts"
    extscache_folder = build_root / "extscache"

    cmd, stubbed = _build_command(
        kit_exe=kit_exe,
        app=args.app,
        ext_names=args.ext,
        ext_folder=ext_folder,
        extscache_folder=extscache_folder,
        portable_root=build_root,
    )

    if not stubbed:
        print(
            "[stubgen_schemas] No schema extension build dirs found; "
            "nothing to stub."
        )
        return 0

    print(f"[stubgen_schemas] Stubbing schemas: {', '.join(stubbed)}")
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
