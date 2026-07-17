# /// script
# requires-python = ">=3.11"
# dependencies = ["python-dotenv>=1.0", "watchfiles>=1.0"]
# ///
"""Development helpers for working on ItemVersion against a local WoW install.

Usage: uv run scripts/dev.py <command>, or `help` for the list.

The WoW root is the directory containing _retail_, _classic_ and friends. Set
WOW_ROOT once in .env (gitignored), or pass it as an environment variable.

The locale checker needs luaparser and the packaging steps need release.sh, so
both stay separate and this shells out to them.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Literal

from dotenv import load_dotenv  # type: ignore[ty:unresolved-import]
from watchfiles import Change, watch  # type: ignore[ty:unresolved-import]

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = "ItemVersion"

# Link to the source dir rather than the build output. It is a stable path, so it
# cannot rot the way a version-stamped dist/ path does, and an edit is live on the
# next /reload with no build step. The tradeoff is that packager keywords stay
# unexpanded.
LINK_SRC = REPO_ROOT / SOURCE_DIR
LIBS_DIR = LINK_SRC / "Libs"
ENV_FILE = REPO_ROOT / ".env"

BUILD_ROOT = REPO_ROOT / ".release"
BUILD_LIBS_DIR = BUILD_ROOT / SOURCE_DIR / "Libs"

FLAVORS = ("_retail_", "_classic_era_", "_classic_", "_anniversary_")

# Each declares its own dependencies inline, so uv runs them without a venv.
TEST_SCRIPTS = ("scripts/test_locales.py", "scripts/test_dev.py")

# What watch re-lints on. The addon is Lua plus the TOC and the XML that lists the
# libraries and widgets.
WATCH_SUFFIXES = (".lua", ".toc", ".xml")

State = Literal["absent", "link-ok", "link-broken", "real-dir"]


class Die(Exception):
    """A fatal, already-explained error. main turns this into exit 1."""


def report(label: str, message: str) -> None:
    print(f"  {label:<14} {message}")


def resolve_wow_root(value: str | None) -> Path:
    if not value:
        raise Die(
            "no WoW root configured.\n"
            "Copy the template and set WOW_ROOT for your machine:\n"
            "  cp .env.template .env\n"
            "or pass it directly:\n"
            "  WOW_ROOT='/path/to/World of Warcraft' uv run scripts/dev.py install"
        )

    path = Path(value)
    if not path.is_dir():
        raise Die(f"not a directory: {path}")

    return path


def wow_root() -> Path:
    # load_dotenv does not overwrite a variable that is already set, so a real
    # environment variable still wins over .env and a one-off run can point
    # somewhere else without editing the file.
    load_dotenv(ENV_FILE)
    return resolve_wow_root(os.environ.get("WOW_ROOT"))


def require_libs() -> None:
    if not LIBS_DIR.is_dir():
        raise Die(
            f"{SOURCE_DIR}/Libs is missing, so the addon would fail to load.\n"
            "Fetch the Ace3 externals first:\n"
            "  uv run scripts/dev.py libs"
        )


def addons_dir_for(root: Path, flavor: str) -> Path:
    return root / flavor / "Interface" / "AddOns"


def target_for(root: Path, flavor: str) -> Path:
    return addons_dir_for(root, flavor) / SOURCE_DIR


def classify(target: Path) -> State:
    """What is sitting at a target path.

    is_symlink is tested first, since exists and is_dir both follow symlinks.
    """
    if target.is_symlink():
        return "link-ok" if target.exists() else "link-broken"
    if target.is_dir():
        return "real-dir"
    return "absent"


def version_from_toc(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("## Version:"):
            return line.removeprefix("## Version:").strip()
    return None


def installed_version_at(target: Path) -> str | None:
    toc = target / f"{SOURCE_DIR}.toc"
    try:
        return version_from_toc(toc.read_text(encoding="utf-8"))
    except OSError:
        return None


def link(src: Path, dst: Path) -> None:
    """Point dst at src, replacing an existing symlink rather than following it."""
    if dst.is_symlink():
        dst.unlink()
    os.symlink(src, dst, target_is_directory=True)


def cmd_install() -> int:
    root = wow_root()
    require_libs()

    linked = 0

    for flavor in FLAVORS:
        addons = addons_dir_for(root, flavor)
        target = target_for(root, flavor)

        if not addons.is_dir():
            report(flavor, "skip, no AddOns dir")
            continue

        # A real directory is someone else's install. Deleting it is the user's call.
        if classify(target) == "real-dir":
            report(flavor, "REFUSED, a real directory is installed there")
            report("", f"remove it yourself, then re-run: {target}")
            continue

        try:
            link(LINK_SRC, target)
        except OSError as error:
            # Windows only grants symlink rights to admins, or to anyone with
            # Developer Mode on. Nothing here can fix that for the user, so say so
            # rather than dumping WinError 1314.
            if getattr(error, "winerror", None) == 1314:
                raise Die(
                    "Windows would not let us create a symlink.\n"
                    "Turn on Developer Mode (Settings > System > For developers),\n"
                    "or run this from an Administrator terminal."
                ) from error
            raise Die(f"could not link {target}: {error}") from error

        report(flavor, "linked")
        linked += 1

    print(f"Linked {linked} flavor(s) to {SOURCE_DIR}/. Use /reload in game to pick up edits.")
    return 0


def cmd_uninstall() -> int:
    root = wow_root()

    for flavor in FLAVORS:
        target = target_for(root, flavor)
        state = classify(target)

        if state in ("link-ok", "link-broken"):
            target.unlink()
            report(flavor, "unlinked")
        elif state == "real-dir":
            report(flavor, "left alone, real directory not a symlink")

    return 0


def cmd_status() -> int:
    root = wow_root()
    print(f"WOW_ROOT: {root}")

    for flavor in FLAVORS:
        target = target_for(root, flavor)
        state = classify(target)

        if state == "link-ok":
            report(flavor, f"symlink -> {os.readlink(target)}")
        elif state == "link-broken":
            report(flavor, f"BROKEN symlink -> {os.readlink(target)}")
        elif state == "real-dir":
            report(flavor, f"real directory, version {installed_version_at(target)}")
        else:
            report(flavor, "not installed")

    return 0


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


# selene and stylua resolve their config (selene.toml, stylua.toml, .styluaignore)
# relative to the cwd, so run from the repo root. Nothing here short-circuits: one
# run should report everything that is wrong.
def cmd_check() -> int:
    require_tool("selene")
    require_tool("stylua")
    require_tool("uv")

    failed = 0

    if run(["selene", SOURCE_DIR]) != 0:
        failed = 1

    if run(["stylua", "--check", SOURCE_DIR]) == 0:
        print("stylua: no changes needed")
    else:
        print("stylua: formatting needed, run the format command")
        failed = 1

    # --check so this never edits from a check run. The locales command is the mode
    # that writes.
    if run(["uv", "run", "scripts/locales.py", "--check"]) != 0:
        failed = 1

    return failed


# Prunes stale keys, sorts, and stubs out anything untranslated. uv fetches the
# script's dependencies itself, so there is no venv to set up.
def cmd_locales() -> int:
    require_tool("uv")
    return run(["uv", "run", "scripts/locales.py"])


def cmd_test() -> int:
    require_tool("uv")

    failed = 0
    for script in TEST_SCRIPTS:
        if run(["uv", "run", script]) != 0:
            failed = 1

    return failed


def cmd_format() -> int:
    require_tool("stylua")
    failed = run(["stylua", SOURCE_DIR])
    if failed == 0:
        print(f"formatted {SOURCE_DIR}")
    return failed


def is_watched(path: str) -> bool:
    """True for the addon sources worth re-linting on save.

    Libs is vendored Ace3 that we never edit and selene skips anyway, and it is
    large enough that watching it is wasted work.
    """
    candidate = Path(path)

    if LIBS_DIR == candidate or LIBS_DIR in candidate.parents:
        return False

    return candidate.suffix in WATCH_SUFFIXES


def clear_screen() -> None:
    # Cheaper than shelling out to clear/cls, and Windows terminals have handled
    # these since Windows 10.
    print("\033[2J\033[H", end="")


def describe(changes: Iterable[tuple[Change, str]]) -> list[str]:
    return sorted(f"{change.name} {relative(Path(path))}" for change, path in changes)


# There is no build step to run here: install symlinks the source dir, so a save is
# already live in game. All this does is lint, so a mistake surfaces before you
# alt-tab and reload.
def cmd_watch() -> int:
    clear_screen()
    cmd_check()

    # debounce is milliseconds. A save often lands as several events, and one lint
    # per burst is the point.
    for changes in watch(LINK_SRC, watch_filter=lambda _, path: is_watched(path), debounce=200):
        clear_screen()
        for line in describe(changes):
            print(line)
        print()
        cmd_check()

    return 0


# The BigWigs packager owns fetching externals and building the zip, so these
# shell out to it rather than reimplement it. -z skips the zip, -e skips the
# externals checkout.
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


def relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def cmd_help() -> int:
    build_parser().print_help()
    return 0


COMMANDS = {
    "libs": (cmd_libs, f"Fetch the Ace3 externals into {SOURCE_DIR}/Libs."),
    "build": (cmd_build, "Package a release build into .release/."),
    "clean": (cmd_clean, "Remove .release/ and the fetched Libs."),
    "install": (cmd_install, f"Symlink {SOURCE_DIR}/ into each WoW flavor's AddOns dir."),
    "uninstall": (cmd_uninstall, "Remove our symlinks. Never touches a real directory."),
    "status": (cmd_status, "Show what is installed for each flavor."),
    "check": (cmd_check, "Lint, check formatting, and check the locale files. Writes nothing."),
    "format": (cmd_format, "Reformat the addon with stylua."),
    "locales": (cmd_locales, "Prune, sort and stub the locale files. This one writes."),
    "test": (cmd_test, "Run the tests for the dev tooling."),
    "watch": (cmd_watch, "Re-run check on every save. Reload in game to see changes."),
    "help": (cmd_help, "Show this message."),
}

EPILOG = (
    "The WoW root comes from the WOW_ROOT env var, else from .wowroot.\n"
    "See .wowroot.template."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dev.py",
        description=__doc__.splitlines()[0],
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    for name, (_, help_text) in COMMANDS.items():
        subparsers.add_parser(name, help=help_text)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    handler, _ = COMMANDS[args.command]

    try:
        return handler()
    except Die as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        # Ctrl-C out of watch is how you are meant to leave it, so do not make it
        # look like a crash.
        print()
        return 130


if __name__ == "__main__":
    sys.exit(main())
