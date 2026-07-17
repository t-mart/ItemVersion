"""Fetching the Ace3 externals and building a release, via the BigWigs packager."""

from __future__ import annotations

import shutil

from common import LIBS_DIR, REPO_ROOT, SOURCE_DIR, relative, require_tool, run

BUILD_ROOT = REPO_ROOT / ".release"
BUILD_LIBS_DIR = BUILD_ROOT / SOURCE_DIR / "Libs"


# The packager owns fetching externals and building the zip, so these shell out to
# it rather than reimplement it. -z skips the zip, -e skips the externals checkout.
def cmd_libs() -> int:
    if LIBS_DIR.is_dir():
        print(f"{SOURCE_DIR}/Libs is already present. Run clean first to refetch.")
        return 0

    require_tool("release.sh")

    failed = run(["release.sh", "-z"])
    if failed != 0:
        return failed

    shutil.copytree(BUILD_LIBS_DIR, LIBS_DIR)
    print(f"fetched {SOURCE_DIR}/Libs")
    return 0


def cmd_build() -> int:
    require_tool("release.sh")
    return run(["release.sh", "-ze"])


def cmd_clean() -> int:
    for path in (BUILD_ROOT, LIBS_DIR):
        if path.is_dir():
            shutil.rmtree(path)
            print(f"removed {relative(path)}")

    return 0
