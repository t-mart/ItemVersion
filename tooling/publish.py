"""Publishing a built addon to CurseForge and GitHub.

build makes the zip; this ships it. CurseForge and GitHub are independent targets
chosen with --to, and everything a target receives is derived from the version and
the release type in one place, so the two can never describe the same build
differently.

A release goes to both and reuses the git tag the release workflow already made.
Alpha and beta go to CurseForge only, make no git changes, and carry a timestamp in
their label so they sort after the release they were cut from. Nothing uploads until
you have seen the plan: --dry-run prints it and stops, and without --yes there is a
confirmation prompt.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv  # type: ignore[ty:unresolved-import]

from common import REPO_ROOT, Die, relative, require_tool, run
from config import Config, load_config
from interfaces import version_from_interface
from packaging import BUILD_ROOT
from toc import require_version, toc_field

ENV_FILE = REPO_ROOT / ".env"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

CF_HOST = "https://wow.curseforge.com"
CF_TOKEN_ENV = "CURSEFORGE_TOKEN"

RELEASE, ALPHA, BETA = "release", "alpha", "beta"
RELEASE_TYPES = (RELEASE, ALPHA, BETA)

CURSEFORGE, GITHUB = "curseforge", "github"
TARGETS = (CURSEFORGE, GITHUB)

DEFAULT_NOTES = "Automated release."


@dataclass(frozen=True)
class Plan:
    release_type: str
    display_name: str  # the CurseForge label and the GitHub release title
    tag: str  # the git tag a GitHub release hangs off
    archive: Path
    version_names: tuple[str, ...]  # CurseForge game versions, e.g. 12.0.7
    notes: str


def default_targets(release_type: str) -> tuple[str, ...]:
    return TARGETS if release_type == RELEASE else (CURSEFORGE,)


def interface_list(text: str) -> tuple[str, ...]:
    listed = toc_field(text, "Interface")
    if not listed:
        raise Die("the TOC has no ## Interface line")
    return tuple(part.strip() for part in listed.split(",") if part.strip())


def release_notes(changelog: str) -> str:
    """The body of the top section of the changelog, heading dropped.

    That section is the pending "Unreleased" notes, which is what this release
    contains. An empty section (a bare data refresh) falls back to a default.
    """
    lines = changelog.splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("## ")), None)
    if start is None:
        return DEFAULT_NOTES

    body = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)

    notes = "\n".join(body).strip()
    return notes or DEFAULT_NOTES


def build_plan(
    config: Config,
    version: str,
    interfaces: tuple[str, ...],
    release_type: str,
    notes: str,
    when: datetime,
) -> Plan:
    if release_type == RELEASE:
        display_name = version
    else:
        display_name = f"{version}-{release_type}.{when.strftime('%Y%m%d%H%M%S')}"

    return Plan(
        release_type=release_type,
        display_name=display_name,
        tag=version,
        archive=BUILD_ROOT / f"{config.name}-{version}.zip",
        version_names=tuple(version_from_interface(i) for i in interfaces),
        notes=notes,
    )


def _get_json(url: str, token: str) -> object:
    request = urllib.request.Request(url, headers={"X-Api-Token": token})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise Die(f"CurseForge returned {error.code} for {url}") from error
    except OSError as error:
        raise Die(f"could not reach {url}: {error}") from error


def resolve_version_ids(catalog: object, names: tuple[str, ...]) -> list[int]:
    """Map game-version names to CurseForge ids, failing on any it does not know."""
    if not isinstance(catalog, list):
        raise Die("CurseForge game versions response was not a list")

    by_name: dict[str, int] = {}
    for entry in catalog:
        if not isinstance(entry, dict):
            continue
        name, identifier = entry.get("name"), entry.get("id")
        if isinstance(name, str) and isinstance(identifier, int):
            by_name.setdefault(name, identifier)

    ids = [by_name[name] for name in names if name in by_name]
    missing = [name for name in names if name not in by_name]
    if missing:
        raise Die(
            "CurseForge does not list game version(s): "
            + ", ".join(missing)
            + ". It may not have caught up to this patch yet."
        )
    return ids


def _multipart(fields: dict[str, str], filename: str, file_bytes: bytes) -> tuple[str, bytes]:
    boundary = f"----ItemVersion{uuid.uuid4().hex}"
    parts = []
    for name, value in fields.items():
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            f"{value}\r\n".encode("utf-8")
        )
    parts.append(
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/zip\r\n\r\n".encode("utf-8")
    )
    parts.append(file_bytes)
    parts.append(f"\r\n--{boundary}--\r\n".encode("utf-8"))
    return boundary, b"".join(parts)


def cf_token() -> str:
    load_dotenv(ENV_FILE)
    token = os.environ.get(CF_TOKEN_ENV)
    if not token:
        raise Die(
            f"no CurseForge token. Set {CF_TOKEN_ENV} in .env or the environment."
        )
    return token


def upload_curseforge(config: Config, plan: Plan) -> None:
    token = cf_token()
    catalog = _get_json(f"{CF_HOST}/api/game/versions", token)
    version_ids = resolve_version_ids(catalog, plan.version_names)

    metadata = json.dumps(
        {
            "displayName": plan.display_name,
            "gameVersions": version_ids,
            "releaseType": plan.release_type,
            "changelog": plan.notes,
            "changelogType": "markdown",
        }
    )
    boundary, body = _multipart(
        {"metadata": metadata}, plan.archive.name, plan.archive.read_bytes()
    )

    url = f"{CF_HOST}/api/projects/{config.curseforge_project_id}/upload-file"
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "X-Api-Token": token,
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            response.read()
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")
        raise Die(f"CurseForge upload failed ({error.code}): {detail}") from error
    except OSError as error:
        raise Die(f"CurseForge upload failed: {error}") from error

    print(f"  uploaded {plan.archive.name} to CurseForge as {plan.release_type}")


def upload_github(plan: Plan) -> None:
    require_tool("gh")
    failed = run(
        [
            "gh",
            "release",
            "create",
            plan.tag,
            str(plan.archive),
            "--title",
            plan.display_name,
            "--notes",
            plan.notes,
        ]
    )
    if failed:
        raise Die("gh release create failed")
    print(f"  created GitHub release {plan.tag}")


def print_plan(plan: Plan, targets: tuple[str, ...], config: Config) -> None:
    print(f"Release type: {plan.release_type}")
    print(f"Archive:      {relative(plan.archive)}")
    if CURSEFORGE in targets:
        print(f"CurseForge:   project {config.curseforge_project_id}")
        print(f"  label       {plan.display_name}")
        print(f"  versions    {', '.join(plan.version_names)}")
    if GITHUB in targets:
        print(f"GitHub:       release {plan.tag}")
    print("Notes:")
    for line in plan.notes.splitlines() or [""]:
        print(f"  {line}")


def _confirm() -> bool:
    try:
        answer = input("Proceed? [y/N] ")
    except EOFError:
        return False
    return answer.strip().lower().startswith("y")


def cmd_publish(
    type: str = RELEASE,
    to: list[str] | None = None,
    dry_run: bool = False,
    yes: bool = False,
) -> int:
    config = load_config()
    targets = tuple(to) if to else default_targets(type)

    toc = config.toc_path.read_text(encoding="utf-8")
    plan = build_plan(
        config,
        require_version(toc),
        interface_list(toc),
        type,
        release_notes(CHANGELOG.read_text(encoding="utf-8")),
        datetime.now(timezone.utc),
    )

    if not plan.archive.exists():
        raise Die(f"{relative(plan.archive)} is not built yet. Run ./dev build first.")

    print_plan(plan, targets, config)

    if dry_run:
        return 0
    if not yes and not _confirm():
        print("aborted, nothing uploaded", file=sys.stderr)
        return 1

    for target in targets:
        if target == CURSEFORGE:
            upload_curseforge(config, plan)
        elif target == GITHUB:
            upload_github(plan)

    return 0
