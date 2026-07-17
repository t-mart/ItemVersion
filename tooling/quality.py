"""Linting, formatting, the locale checker, the tests, and the watch loop."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from watchfiles import Change, watch  # type: ignore[ty:unresolved-import]

import locales
from common import relative, require_tool, run
from config import load_config

# The tests declare their dependencies inline, so uv runs them without a venv.
# They are the one thing not imported: pytest belongs to the tests, not to ./dev.
TEST_RUNNER = "tooling/run_tests.py"

# What watch re-lints on. The addon is Lua plus the TOC and the XML that lists the
# libraries and widgets.
WATCH_SUFFIXES = (".lua", ".toc", ".xml")


# selene and stylua resolve their config (selene.toml, stylua.toml, .styluaignore)
# relative to the cwd, so run from the repo root. Nothing here short-circuits: one
# run should report everything that is wrong.
def cmd_check() -> int:
    require_tool("selene")
    require_tool("stylua")

    source = relative(load_config().source_dir)
    failed = 0

    if run(["selene", source]) != 0:
        failed = 1

    if run(["stylua", "--check", source]) == 0:
        print("stylua: no changes needed")
    else:
        print("stylua: formatting needed, run the format command")
        failed = 1

    # --check so this never edits from a check run. The locales command is the mode
    # that writes.
    if locales.main(["--check"]) != 0:
        failed = 1

    return failed


# Prunes stale keys, sorts, and stubs out anything untranslated.
def cmd_locales() -> int:
    return locales.main([])


def cmd_test() -> int:
    require_tool("uv")
    return run(["uv", "run", TEST_RUNNER])


def cmd_format() -> int:
    require_tool("stylua")
    source = relative(load_config().source_dir)
    failed = run(["stylua", source])
    if failed == 0:
        print(f"formatted {source}")
    return failed


def is_watched(path: str, libs_dir: Path) -> bool:
    """True for the addon sources worth re-linting on save.

    Libs is vendored Ace3 that we never edit and selene skips anyway, and it is
    large enough that watching it is wasted work.
    """
    candidate = Path(path)

    if libs_dir == candidate or libs_dir in candidate.parents:
        return False

    return candidate.suffix in WATCH_SUFFIXES


def describe(changes: Iterable[tuple[Change, str]]) -> list[str]:
    return sorted(f"{change.name} {relative(Path(path))}" for change, path in changes)


# There is no build step to run here: install symlinks the source dir, so a save is
# already live in game. All this does is lint, so a mistake surfaces before you
# alt-tab and reload.
def cmd_watch() -> int:
    config = load_config()
    print(f"watching {relative(config.source_dir)} for changes...")
    cmd_check()

    # debounce is milliseconds. A save often lands as several events, and one lint
    # per burst is the point.
    for changes in watch(
        config.source_dir,
        watch_filter=lambda _, path: is_watched(path, config.libs_dir),
        debounce=200,
    ):
        for line in describe(changes):
            print(line)
        print()
        cmd_check()

    return 0
