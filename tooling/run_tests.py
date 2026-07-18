# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "jsonschema>=4.0",
#   "luaparser>=3.2.1",
#   "pytest>=8",
#   "python-dotenv>=1.0",
#   "pyyaml>=6.0",
#   "watchfiles>=1.0",
# ]
# ///
"""Run the tests for the dev tooling.

  ./dev test
  uv run tooling/run_tests.py -k Interfaces    to run a subset

The test files declare no dependencies of their own. This is the one place that
lists them, and pytest collects tooling/tests from here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest  # type: ignore[ty:unresolved-import]

TESTS = Path(__file__).resolve().parent / "tests"

if __name__ == "__main__":
    # Importing the modules under test pulls in watchfiles, and so anyio, before
    # pytest can rewrite the assertions in anyio's plugin. We do not test anyio,
    # so the warning is only noise.
    ignore_anyio = "ignore::pytest.PytestAssertRewriteWarning"
    sys.exit(pytest.main([str(TESTS), "-q", "-W", ignore_anyio, *sys.argv[1:]]))
