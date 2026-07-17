"""Linking the addon into a local WoW install, and saying what is linked.

The WoW root is the directory containing _retail_, _classic_ and friends. Set
WOW_ROOT once in .env (gitignored), or pass it as an environment variable.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv  # type: ignore[ty:unresolved-import]

from common import LIBS_DIR, LINK_SRC, REPO_ROOT, SOURCE_DIR, Die, report
from toc import version_from_toc

ENV_FILE = REPO_ROOT / ".env"

# The names a user types map to the directory WoW actually uses.
FLAVOR_DIRS = {
    "retail": "_retail_",
    "classic-era": "_classic_era_",
    "classic": "_classic_",
    "anniversary": "_anniversary_",
}

# Directory names, in a stable order, for the commands that touch every flavor.
FLAVORS = tuple(FLAVOR_DIRS.values())

ALL_FLAVORS = "all"

State = Literal["absent", "link-ok", "link-broken", "real-dir"]


def selected_flavors(flavors: list[str] | None) -> tuple[str, ...]:
    """Directory names to install into, from the --flavor selection.

    No selection means all of them, as does an explicit "all". Naming "all"
    alongside a specific flavor is contradictory, so refuse it.
    """
    chosen = flavors or [ALL_FLAVORS]
    if ALL_FLAVORS in chosen:
        if set(chosen) != {ALL_FLAVORS}:
            raise Die("--flavor all installs everywhere; do not name others with it")
        return FLAVORS
    return tuple(FLAVOR_DIRS[name] for name in chosen)


def resolve_wow_root(value: str | None) -> Path:
    if not value:
        raise Die(
            "no WoW root configured.\n"
            "Copy the template and set WOW_ROOT for your machine:\n"
            "  cp .env.template .env\n"
            "or pass it directly:\n"
            "  WOW_ROOT='/path/to/World of Warcraft' ./dev install"
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
            "  ./dev libs"
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


def cmd_install(flavors: list[str] | None = None) -> int:
    root = wow_root()
    require_libs()

    linked = 0

    for flavor in selected_flavors(flavors):
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

    print(
        f"Installed symlinks into {linked} flavor(s) to {SOURCE_DIR}/. "
        "Use /reload in game to pick up edits."
    )
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


def cmd_install_status() -> int:
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
