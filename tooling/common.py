"""Paths and plumbing shared by the ./dev commands."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = "ItemVersion"

# Link to the source dir rather than the build output. It is a stable path, so it
# cannot rot the way a version-stamped dist/ path does, and an edit is live on the
# next /reload with no build step. The tradeoff is that packager keywords stay
# unexpanded.
LINK_SRC = REPO_ROOT / SOURCE_DIR
LIBS_DIR = LINK_SRC / "Libs"
TOC_PATH = LINK_SRC / f"{SOURCE_DIR}.toc"


class Die(Exception):
    """A fatal, already-explained error. main turns this into exit 1."""


def report(label: str, message: str) -> None:
    print(f"  {label:<14} {message}")


def relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def require_tool(name: str) -> str:
    found = shutil.which(name)
    if not found:
        raise Die(f"{name} is not installed.")
    return found


def run(command: list[str]) -> int:
    # Our prints are buffered, a child's writes to the same terminal are not. Into
    # a pipe that reorders the report, putting our lines after output they were
    # meant to introduce. Flushing first keeps the two interleaved as written.
    sys.stdout.flush()
    return subprocess.run(command, cwd=REPO_ROOT).returncode
