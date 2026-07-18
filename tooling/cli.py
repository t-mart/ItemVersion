"""Development helpers for working on ItemVersion against a local WoW install.

The command line behind ./dev, which is the entry point and owns the dependencies.
The commands themselves live beside this: install.py, interfaces.py, packaging.py
and quality.py.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from typing import Callable

from common import Die
from data import cmd_get_item_data
from install import (
    ALL_FLAVORS,
    FLAVOR_DIRS,
    cmd_install,
    cmd_install_status,
    cmd_uninstall,
)
from interfaces import cmd_interfaces
from packaging import cmd_build, cmd_clean, cmd_prepare
from publish import RELEASE, RELEASE_TYPES, TARGETS, cmd_publish
from quality import cmd_check, cmd_format, cmd_locales, cmd_test, cmd_watch


def cmd_help() -> int:
    build_parser().print_help()
    return 0


@dataclass(frozen=True)
class Command:
    handler: Callable[..., int]
    help: str
    # Adds the command's own options. Whatever it declares is passed to the
    # handler as a keyword argument, so the two cannot drift apart.
    configure: Callable[[argparse.ArgumentParser], None] | None = None


def interfaces_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="say what would be written, but leave the TOC alone",
    )


def publish_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--type",
        choices=RELEASE_TYPES,
        default=RELEASE,
        help="the CurseForge release type (default: release)",
    )
    parser.add_argument(
        "--to",
        action="append",
        choices=TARGETS,
        metavar="TARGET",
        help=(
            "publish to this target; may be repeated. "
            f"one of {', '.join(TARGETS)}. Defaults by type: "
            "release goes everywhere, alpha and beta to curseforge only."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the plan and stop, uploading nothing",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="skip the confirmation prompt (for CI)",
    )


def install_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--flavor",
        dest="flavors",
        action="append",
        choices=(*FLAVOR_DIRS, ALL_FLAVORS),
        metavar="FLAVOR",
        help=(
            "install into this flavor only; may be repeated. one of "
            f"{', '.join(FLAVOR_DIRS)}, or {ALL_FLAVORS} (the default)."
        ),
    )


COMMANDS = {
    "interfaces": Command(
        cmd_interfaces,
        "Update the TOC's Interface line from Blizzard.",
        interfaces_options,
    ),
    "prepare": Command(
        cmd_prepare, "Fetch the embedded libraries and generate the locale files."
    ),
    "get-item-data": Command(
        cmd_get_item_data,
        "Download the latest ItemData.lua from item-version-scrape",
    ),
    "build": Command(cmd_build, "Package the addon zip into dist/."),
    "clean": Command(cmd_clean, "Remove dist/ and the generated Libs and Locales."),
    "install": Command(
        cmd_install,
        "Symlink the addon into each WoW flavor's AddOns dir.",
        install_options,
    ),
    "uninstall": Command(cmd_uninstall, "Remove our symlinks."),
    "publish": Command(
        cmd_publish,
        "Upload a built zip to CurseForge and GitHub.",
        publish_options,
    ),
    "install-status": Command(
        cmd_install_status, "Show what is installed for each flavor."
    ),
    "check": Command(
        cmd_check, "Lint, check formatting, and check the locale files. Writes nothing."
    ),
    "format": Command(cmd_format, "Reformat the addon with stylua."),
    "locales": Command(
        cmd_locales, "Reconcile translations.yml with the code. This one writes."
    ),
    "test": Command(cmd_test, "Run the tests for the dev tooling."),
    "watch": Command(
        cmd_watch, "Re-run check on every save. Reload in game to see changes."
    ),
    "help": Command(cmd_help, "Show this message."),
}

EPILOG = "Some subcommands may use environment variables, and .env is supported.\nSee .env.template."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="./dev",
        description=__doc__.splitlines()[0],
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    for name, command in COMMANDS.items():
        subparser = subparsers.add_parser(name, help=command.help)
        if command.configure:
            command.configure(subparser)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    command = COMMANDS[args.command]
    options = {name: value for name, value in vars(args).items() if name != "command"}

    try:
        return command.handler(**options)
    except Die as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        # Ctrl-C out of watch is how you are meant to leave it, so do not make it
        # look like a crash.
        print()
        return 130
