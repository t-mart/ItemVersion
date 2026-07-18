"""Linking or copying the addon into a local WoW install, and saying what is there.

The WoW root is the directory containing _retail_, _classic_ and friends. Set
WOW_ROOT once in .env (gitignored), or pass it as an environment variable.

There are three sources to install from:
  - local (the default): symlink the working source, so edits live-reload.
  - gh: download a published GitHub release by tag and copy it in.
  - cf: download a published CurseForge file by id and copy it in.

The remote sources let you test the exact bytes users get, not just your working
tree. They land as real directories, each carrying a small marker file so status,
uninstall and a re-install can tell our copy from a foreign install.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from zipfile import ZipFile

from dotenv import load_dotenv  # type: ignore[ty:unresolved-import]

from common import REPO_ROOT, Die, report, require_tool, run
from config import Config, load_config
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

# The sources an install can draw from.
LOCAL, GH, CF = "local", "gh", "cf"

# Left inside a copied install so status, uninstall and a re-install can tell our
# own dev copy from a foreign directory that happens to sit at the target. A
# symlink is self-evidently ours; a real directory needs this to say so.
MARKER = ".dev-install"

# CurseForge's public per-file download. It 302s to the CDN, which urllib follows
# on its own, and needs no auth for a file the author has already published.
CF_DOWNLOAD_URL = (
    "https://www.curseforge.com/api/v1/mods/{project_id}/files/{file_id}/download"
)
USER_AGENT = "ItemVersion-dev-install"

State = Literal["absent", "link-ok", "link-broken", "real-dir"]


@dataclass(frozen=True)
class Source:
    mode: str  # LOCAL, GH or CF
    ref: str | None  # gh tag (None or "latest" means latest), cf file id, None for local


def resolve_source(local: bool = False, gh: str | None = None, cf: int | None = None) -> Source:
    """Which source to install from, out of the mutually exclusive flags.

    None given means local, as does an explicit --local. The flags are exclusive
    at the CLI, so at most one of cf and gh is ever set.
    """
    if cf is not None:
        return Source(CF, str(cf))
    if gh is not None:
        return Source(GH, gh)
    return Source(LOCAL, None)


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


def require_prepared(config: Config) -> None:
    """The generated bits a symlinked install needs, or a pointer to prepare.

    Libs and the locale files are gitignored output, so a fresh checkout has
    neither, and the addon would fail to load without them. A downloaded build
    already carries both, so this only guards the local source.
    """
    missing = []
    if not config.libs_dir.is_dir():
        missing.append("the embedded libraries")
    if not (config.locales_dir / "enUS.lua").is_file():
        missing.append("the locale files")

    if missing:
        raise Die(
            f"{config.name} is missing {' and '.join(missing)}, so it would fail to load.\n"
            "Generate them first:\n"
            "  ./dev prepare"
        )


def addons_dir_for(root: Path, flavor: str) -> Path:
    return root / flavor / "Interface" / "AddOns"


def target_for(root: Path, flavor: str, name: str) -> Path:
    return addons_dir_for(root, flavor) / name


def classify(target: Path) -> State:
    """What is sitting at a target path.

    is_symlink is tested first, since exists and is_dir both follow symlinks.
    """
    if target.is_symlink():
        return "link-ok" if target.exists() else "link-broken"
    if target.is_dir():
        return "real-dir"
    return "absent"


def is_our_copy(target: Path) -> bool:
    """Whether a real directory at target is a dev copy we placed."""
    return not target.is_symlink() and target.is_dir() and (target / MARKER).is_file()


def read_marker(target: Path) -> dict | None:
    """The marker a dev copy left, or None if there is none or it is unreadable."""
    try:
        return json.loads((target / MARKER).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def write_marker(config: Config, target: Path, source: Source) -> None:
    data = {
        "source": source.mode,
        "ref": source.ref,
        "version": installed_version_at(target, config.name),
        "installed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    (target / MARKER).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def installed_version_at(target: Path, name: str) -> str | None:
    toc = target / f"{name}.toc"
    try:
        return version_from_toc(toc.read_text(encoding="utf-8"))
    except OSError:
        return None


def link(src: Path, dst: Path) -> None:
    """Point dst at src, replacing an existing symlink rather than following it."""
    if dst.is_symlink():
        dst.unlink()
    os.symlink(src, dst, target_is_directory=True)


def remove_target(target: Path) -> None:
    """Clear whatever is at target: unlink a symlink, remove a real directory."""
    if target.is_symlink():
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)


def download_gh(config: Config, tag: str | None, dest_dir: Path) -> Path:
    """Download a release's addon zip from GitHub, returning the local zip path.

    No tag (or the literal "latest") takes the latest release. gh infers the repo
    from the checkout's origin, the same way publish does.
    """
    require_tool("gh")

    command = ["gh", "release", "download"]
    if tag and tag != "latest":
        command.append(tag)
    command += ["--pattern", f"{config.name}-*.zip", "--dir", str(dest_dir), "--clobber"]

    if run(command) != 0:
        raise Die("gh release download failed")

    zips = sorted(dest_dir.glob(f"{config.name}-*.zip"))
    if not zips:
        raise Die(f"no {config.name}-*.zip found in that release")
    return zips[-1]


def download_cf(config: Config, file_id: str, dest_dir: Path) -> Path:
    """Download a CurseForge file by id, returning the local zip path."""
    url = CF_DOWNLOAD_URL.format(project_id=config.curseforge_project_id, file_id=file_id)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = response.read()
    except urllib.error.HTTPError as error:
        raise Die(f"CurseForge download failed ({error.code}) for file {file_id}") from error
    except OSError as error:
        raise Die(f"could not reach CurseForge for file {file_id}: {error}") from error

    archive = dest_dir / f"cf-{file_id}.zip"
    archive.write_bytes(body)
    return archive


def extract_addon(config: Config, archive: Path, dest_dir: Path) -> Path:
    """Extract the addon zip and return the folder WoW would load.

    The zip holds a single top-level folder named after the addon (see the build),
    so the extracted <name>/ is what gets copied into a flavor.
    """
    extracted = dest_dir / "extracted"
    with ZipFile(archive) as zip_file:
        zip_file.extractall(extracted)

    folder = extracted / config.name
    if not folder.is_dir():
        raise Die(f"{archive.name} has no {config.name}/ folder inside")
    return folder


def acquire(config: Config, source: Source, dest_dir: Path) -> Path:
    """Download and extract a remote source, returning the addon folder to copy."""
    if source.mode == GH:
        archive = download_gh(config, source.ref, dest_dir)
    elif source.mode == CF:
        archive = download_cf(config, source.ref or "", dest_dir)
    else:
        raise Die(f"nothing to download for source {source.mode}")
    return extract_addon(config, archive, dest_dir)


def place(config: Config, source: Source, target: Path, payload: Path | None, force: bool) -> tuple[bool, str]:
    """Install into one flavor. Returns (installed, message for the report line).

    A foreign real directory is someone else's install; only --force removes it.
    Our own installs, a symlink or a marked copy, are always replaced freely so
    iterating stays frictionless.
    """
    if classify(target) == "real-dir" and not is_our_copy(target) and not force:
        return False, "REFUSED, a real directory is here; use --force to replace it"

    if source.mode == LOCAL:
        remove_target(target)
        try:
            link(config.source_dir, target)
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
        return True, "linked"

    assert payload is not None  # a remote source always acquires a payload first
    remove_target(target)
    try:
        shutil.copytree(payload, target)
    except OSError as error:
        raise Die(f"could not copy into {target}: {error}") from error
    write_marker(config, target, source)
    return True, "installed"


def cmd_install(
    flavors: list[str] | None = None,
    local: bool = False,
    gh: str | None = None,
    cf: int | None = None,
    force: bool = False,
) -> int:
    config = load_config()
    root = wow_root()
    source = resolve_source(local, gh, cf)

    if source.mode == LOCAL:
        require_prepared(config)

    with tempfile.TemporaryDirectory() as tmp:
        payload = None if source.mode == LOCAL else acquire(config, source, Path(tmp))

        installed = 0
        for flavor in selected_flavors(flavors):
            target = target_for(root, flavor, config.name)

            if not addons_dir_for(root, flavor).is_dir():
                report(flavor, "skip, no AddOns dir")
                continue

            ok, message = place(config, source, target, payload, force)
            report(flavor, message)
            if ok:
                installed += 1

    if source.mode == LOCAL:
        print(
            f"Installed symlinks into {installed} flavor(s) to {config.name}/. "
            "Use /reload in game to pick up edits."
        )
    else:
        print(
            f"Installed {source.mode} {source.ref or 'latest'} into {installed} flavor(s) "
            f"as {config.name}/. Reload in game, or restart if it was not already installed."
        )
    return 0


def cmd_uninstall() -> int:
    config = load_config()
    root = wow_root()

    for flavor in FLAVORS:
        target = target_for(root, flavor, config.name)
        state = classify(target)

        if state in ("link-ok", "link-broken"):
            target.unlink()
            report(flavor, "unlinked")
        elif state == "real-dir":
            if is_our_copy(target):
                shutil.rmtree(target)
                report(flavor, "removed dev copy")
            else:
                report(flavor, "left alone, real directory not a symlink")

    return 0


def cmd_install_status() -> int:
    config = load_config()
    root = wow_root()
    print(f"WOW_ROOT: {root}")

    for flavor in FLAVORS:
        target = target_for(root, flavor, config.name)
        state = classify(target)

        if state == "link-ok":
            report(flavor, f"symlink -> {os.readlink(target)}")
        elif state == "link-broken":
            report(flavor, f"BROKEN symlink -> {os.readlink(target)}")
        elif state == "real-dir":
            marker = read_marker(target)
            if marker:
                ref = marker.get("ref") or "latest"
                report(flavor, f"dev copy from {marker.get('source')} {ref}, version {marker.get('version')}")
            else:
                version = installed_version_at(target, config.name)
                report(flavor, f"real directory, version {version}")
        else:
            report(flavor, "not installed")

    return 0
