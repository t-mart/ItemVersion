"""Generic plumbing shared by the ./dev commands.

The project layout (the addon name and where its source lives) is not here: it
derives from wowaddon.yml, so it lives on the Config object in config.py.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


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


def capture(command: list[str]) -> tuple[int, str]:
    """Like run, but return the child's stdout too. Its stderr still passes through.

    For a command whose useful output is a single value (gh prints the new release's
    url), so we can echo it in our own words rather than let it scroll past.
    """
    sys.stdout.flush()
    result = subprocess.run(command, cwd=REPO_ROOT, stdout=subprocess.PIPE, text=True)
    return result.returncode, result.stdout
