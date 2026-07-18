"""Linting, formatting, the locale checker, the tests, and the watch loop."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from watchfiles import Change, watch  # type: ignore[ty:unresolved-import]

import locales
import packaging
from common import Die, relative, require_tool, run
from config import CONFIG_FILE, load_config

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


def is_watched(path: str, libs_dir: Path, locales_dir: Path) -> bool:
    """True for the addon sources worth re-linting on save.

    Libs is vendored Ace3 that we never edit, and Locales is generated from
    translations.yml. Watching either is wasted work, and watching Locales would
    trip the watcher on the files a regenerate just wrote.
    """
    candidate = Path(path)

    for generated in (libs_dir, locales_dir):
        if generated == candidate or generated in candidate.parents:
            return False

    return candidate.suffix in WATCH_SUFFIXES


def describe(changes: Iterable[tuple[Change, str]]) -> list[str]:
    return sorted(f"{change.name} {relative(Path(path))}" for change, path in changes)


def _regenerate_locales(config) -> None:
    """Rebuild the locale files, surviving a malformed translations.yml."""
    try:
        locales.generate(config)
        print("regenerated locale files")
    except Die as error:
        print(f"locales: {error}")


def _ensure_libs(config) -> None:
    """Fetch any newly-declared libs, surviving svn being missing or failing."""
    try:
        packaging.ensure_libs(config)
    except Die as error:
        print(f"libs: {error}")


def sync_generated(config, changed: set[Path], translations_path: Path, config_file: Path) -> None:
    """Bring the generated inputs back in line with a batch of changed files.

    A touched translations.yml means the locale files are stale; a touched
    wowaddon.yml may name a lib that is not on disk yet. Only the config is cached,
    so it is dropped before anything re-reads it.
    """
    if translations_path in changed:
        _regenerate_locales(config)

    if config_file in changed:
        load_config.cache_clear()
        _ensure_libs(load_config())


# install symlinks the source dir, so a save to the addon is already live in game;
# all we do there is lint so a mistake surfaces before you alt-tab and reload. The
# two generated inputs are different: a change to translations.yml or wowaddon.yml
# is only live once we regenerate the locale files or fetch the libs it names.
def cmd_watch() -> int:
    config = load_config()
    translations_path = config.translations_path.resolve()
    config_file = CONFIG_FILE.resolve()

    print(f"watching {relative(config.source_dir)}, translations.yml and wowaddon.yml...")
    _regenerate_locales(config)
    cmd_check()

    def keep(_change: Change, path: str) -> bool:
        return (
            Path(path).resolve() in (translations_path, config_file)
            or is_watched(path, config.libs_dir, config.locales_dir)
        )

    # debounce is milliseconds. A save often lands as several events, and one pass
    # per burst is the point.
    for changes in watch(
        config.source_dir,
        config.translations_path,
        CONFIG_FILE,
        watch_filter=keep,
        debounce=200,
    ):
        changed = {Path(path).resolve() for _, path in changes}
        sync_generated(config, changed, translations_path, config_file)

        for line in describe(changes):
            print(line)
        print()
        cmd_check()

    return 0
