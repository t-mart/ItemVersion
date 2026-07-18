"""The project configuration, read from wowaddon.yml at the repo root.

This is the one place that knows the addon's name, where it uploads, which files
to leave out of a build, and where the embedded libraries come from. The build,
publish and libs commands all read it from here.
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
class Config:
    name: str
    curseforge_project_id: int
    ignore: tuple[str, ...]
    libs: tuple[tuple[str, str], ...]  # (folder under Libs, svn url), in file order

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


def parse_config(text: str) -> Config:
    data = yaml.safe_load(text)
    schema.validate(data, "wowaddon", CONFIG_FILE.name)

    # The schema has vouched for the shape, so these accesses are safe.
    return Config(
        name=data["name"],
        curseforge_project_id=data["curseforge-project-id"],
        ignore=tuple(data.get("ignore") or []),
        libs=tuple(data["libs"].items()),
    )


@cache
def load_config() -> Config:
    try:
        text = CONFIG_FILE.read_text(encoding="utf-8")
    except OSError as error:
        raise Die(f"could not read {CONFIG_FILE.name}: {error}") from error
    return parse_config(text)
