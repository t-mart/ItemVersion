"""Linting, formatting, the locale checker, the tests, and the watch loop."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable

from watchfiles import Change, watch  # type: ignore[ty:unresolved-import]

import locales
import packaging
from common import REPO_ROOT, Die, capture, relative, require_tool, run
from config import CONFIG_FILE, load_config

# The tooling tests declare their dependencies inline, so uv runs them without a
# venv. They are the one thing not imported: pytest belongs to the tests, not to ./dev.
TEST_RUNNER = "tooling/run_tests.py"

# The addon's Lua suite runs under busted. WoW ships a customized PUC-Rio Lua 5.1,
# so we target that rock tree rather than whatever the system lua happens to be.
BUSTED_LUA_VERSION = "5.1"

# The busted suite sits outside the addon source and is plain Lua 5.1, not WoW, so
# it lints against its own selene std (tests/busted.yml) via its own config.
TESTS_DIR = "tests"
TESTS_SELENE_CONFIG = "tests/selene.toml"

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

    # The addon lints against wow-stdlib; the tests against their own Lua 5.1 std.
    if run(["selene", source]) != 0:
        failed = 1
    if run(["selene", "--config", TESTS_SELENE_CONFIG, TESTS_DIR]) != 0:
        failed = 1

    # stylua shares one config across both trees; .styluaignore keeps the generated
    # files out.
    if run(["stylua", "--check", source, TESTS_DIR]) == 0:
        print("stylua: no changes needed")
    else:
        print("stylua: formatting needed, run the format command")
        failed = 1

    # --check so this never edits from a check run. The locales command is the mode
    # that writes.
    if locales.main(["--check"]) != 0:
        failed = 1

    if cmd_test() != 0:
        failed = 1

    return failed


# Prunes stale keys, sorts, and stubs out anything untranslated.
def cmd_locales() -> int:
    return locales.main([])


def _find_busted() -> str:
    """The busted launcher, whether it is on PATH or only in a Lua 5.1 rock tree.

    A distro package (Arch's lua51-busted) lands on PATH; `luarocks --local install`
    tucks the launcher into the tree's bin dir instead, so fall back to asking
    luarocks where that is. Either way the launcher pins itself to Lua 5.1.
    """
    on_path = shutil.which("busted")
    if on_path:
        return on_path

    if shutil.which("luarocks"):
        for scope in (["--local"], []):
            code, out = capture(
                ["luarocks", "--lua-version", BUSTED_LUA_VERSION, *scope, "config", "deploy_bin_dir"]
            )
            candidate = Path(out.strip()) / "busted"
            if code == 0 and candidate.is_file():
                return str(candidate)

    raise Die(
        "busted is not installed. Install it against Lua 5.1:\n"
        "  luarocks --lua-version 5.1 install busted\n"
        "or, on Arch, the lua51-busted package."
    )


def cmd_test() -> int:
    """The addon's Lua suite. Reads .busted for the test dir and require path."""
    return run([_find_busted()])


def cmd_test_tooling() -> int:
    require_tool("uv")
    return run(["uv", "run", TEST_RUNNER])


def cmd_format() -> int:
    require_tool("stylua")
    source = relative(load_config().source_dir)
    failed = run(["stylua", source, TESTS_DIR])
    if failed == 0:
        print(f"formatted {source} and {TESTS_DIR}")
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

    tests_dir = REPO_ROOT / TESTS_DIR

    print(f"watching {relative(config.source_dir)}, {TESTS_DIR}, translations.yml and wowaddon.yml...")
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
        tests_dir,
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
