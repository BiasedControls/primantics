# SPDX-FileCopyrightText: Copyright (c) 2023-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
"""Pull OpenUSD, Python, and cmake build-tool dependencies for schema builds."""

import argparse
import logging
import os
import platform
import subprocess

# schema/scripts/setup.py — resolve paths from script location, not cwd
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))


def _get_platform_arch():
    platform_host = platform.system().lower()
    arch = platform.machine()
    if arch == "AMD64":
        arch = "x86_64"
    if platform_host == "darwin":
        platform_host = "macos"
    return "-".join([platform_host, arch])


def _resolve_usd_packman_path(usd_flavor: str, usd_ver: str, python_ver: str) -> str:
    if usd_flavor == "usd-dev":
        return os.path.join(_REPO_ROOT, "deps", "usd-dev.packman.xml")

    usd_python_version = f"{usd_ver}+{python_ver}"
    return os.path.join(_REPO_ROOT, "templates", "packman", usd_flavor, usd_python_version, "usd-deps.packman.xml")


def _setup_dependencies(usd_flavor: str, usd_ver: str, python_ver: str, config: str, build_tools_only: bool):
    packman_path = _resolve_usd_packman_path(usd_flavor, usd_ver, python_ver)

    if not build_tools_only:
        if usd_flavor == "usd-dev":
            logging.getLogger("usd-plugin-samples").info("Pulling Kit-matched USD dev package from %s...", packman_path)
        else:
            logging.getLogger("usd-plugin-samples").info(
                f"Pulling dependencies for {usd_flavor} {usd_ver} Python {python_ver}..."
            )

        if not os.path.exists(packman_path):
            raise RuntimeError(
                f"Requested OpenUSD flavor {usd_flavor} {usd_ver} Python {python_ver} not currently supported "
                f"(missing {packman_path})"
            )

    platform_arch = _get_platform_arch()
    packman_cmd = os.path.join(_REPO_ROOT, "tools", "packman", "packman.cmd")
    packman_sh = os.path.join(_REPO_ROOT, "tools", "packman", "packman")
    packman_exe = packman_cmd if os.name == "nt" else packman_sh

    if not build_tools_only:
        subprocess.run(
            [
                packman_exe,
                "pull",
                packman_path,
                "-p",
                platform_arch,
                "--token",
                f"platform_target_abi={platform_arch}",
                "--token",
                f"config={config}",
            ],
            check=True,
        )


if __name__ == "__main__":
    configs = ["debug", "Debug", "relwithdebinfo", "RelWithDebInfo", "release", "Release"]
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--usd-flavor",
        dest="usd_flavor",
        required=False,
        choices=["nv-usd", "usd-dev"],
        default="usd-dev",
    )
    parser.add_argument("--usd-ver", dest="usd_ver", required=False, default="22.11")
    parser.add_argument("--python-ver", dest="python_ver", required=False, default="3.10")
    parser.add_argument("--config", dest="config", required=False, default="Release", choices=configs)
    parser.add_argument("--build-tools-only", dest="build_tools_only", required=False, action="store_true")
    args = parser.parse_args()

    _setup_dependencies(args.usd_flavor, args.usd_ver, args.python_ver, args.config, args.build_tools_only)
