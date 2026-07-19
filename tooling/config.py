"""The project configuration, read from wowaddon.yml at the repo root.

This is the one place that knows the addon's name, where it uploads, which files
are development-only and never ship, and where the embedded libraries come from.
The build, publish and libs commands all read it from here.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from pathlib import Path

import yaml  # type: ignore[ty:unresolved-import]

import schema
from common import REPO_ROOT, Die

CONFIG_FILE = REPO_ROOT / "wowaddon.yml"

# The addon source lives under here, in a directory named after the addon.
SRC_ROOT = REPO_ROOT / "src"


@dataclass(frozen=True)
class VersionConfig:
    """Where the version lives and the shape bump-calver keeps it in.

    `file` is repo-relative, `pattern` is a regex whose `version` group (or first
    group) locates the version substring, and `format` is a calver template like
    `{YYYY}.{0W}.{N}`. See calver.py for the tokens.
    """

    file: str
    pattern: str
    format: str


@dataclass(frozen=True)
class Config:
    name: str
    curseforge_project_id: int
    # Development-only files: never packaged, and any TOC line referencing them is
    # stripped from the build. Some (Bindings.xml) load in dev via WoW auto-loading;
    # others are listed in the TOC so a symlinked dev install picks them up.
    dev_only: tuple[str, ...]
    libs: tuple[tuple[str, str], ...]  # (folder under Libs, svn url), in file order
    changelog_url: str | None = None
    curseforge_project_slug: str | None = None
    version: VersionConfig | None = None

    # The name is the single source of truth for the layout: the source directory
    # is src/<name>, and WoW requires the TOC basename to match the folder name.
    @property
    def source_dir(self) -> Path:
        return SRC_ROOT / self.name

    @property
    def libs_dir(self) -> Path:
        return self.source_dir / "Libs"

    @property
    def toc_path(self) -> Path:
        return self.source_dir / f"{self.name}.toc"

    @property
    def locales_dir(self) -> Path:
        return self.source_dir / "Locales"

    # The translation source sits beside the addon dir rather than inside it, so it
    # is neither symlinked into a WoW install nor copied into a build.
    @property
    def translations_path(self) -> Path:
        return SRC_ROOT / "translations.yml"

    # bump-calver needs a version block; the rest of the tooling does not, so it
    # stays optional on the config and this is where a missing one is caught.
    @property
    def require_version_config(self) -> VersionConfig:
        if self.version is None:
            raise Die("wowaddon.yml has no `version:` block; add file, pattern and format")
        return self.version


def parse_config(text: str) -> Config:
    data = yaml.safe_load(text)
    schema.validate(data, "wowaddon", CONFIG_FILE.name)

    # The schema has vouched for the shape, so these accesses are safe.
    raw_version = data.get("version")
    version = (
        VersionConfig(
            file=raw_version["file"],
            pattern=raw_version["pattern"],
            format=raw_version["format"],
        )
        if raw_version is not None
        else None
    )

    return Config(
        name=data["name"],
        curseforge_project_id=data["curseforge-project-id"],
        dev_only=tuple(data.get("dev-only") or []),
        libs=tuple(data["libs"].items()),
        changelog_url=data.get("changelog-url"),
        curseforge_project_slug=data.get("curseforge-project-slug"),
        version=version,
    )


@cache
def load_config() -> Config:
    try:
        text = CONFIG_FILE.read_text(encoding="utf-8")
    except OSError as error:
        raise Die(f"could not read {CONFIG_FILE.name}: {error}") from error
    return parse_config(text)
