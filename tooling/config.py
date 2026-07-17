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


def _require(mapping: dict, key: str) -> object:
    if key not in mapping:
        raise Die(f"{CONFIG_FILE.name} is missing '{key}'")
    return mapping[key]


def parse_config(text: str) -> Config:
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise Die(f"{CONFIG_FILE.name} must be a mapping")

    name = _require(data, "name")
    project_id = _require(data, "curseforge-project-id")
    libs = _require(data, "libs")

    if not isinstance(name, str):
        raise Die(f"{CONFIG_FILE.name}: name must be a string")
    if not isinstance(project_id, int):
        raise Die(f"{CONFIG_FILE.name}: curseforge-project-id must be an integer")
    if not isinstance(libs, dict) or not libs:
        raise Die(f"{CONFIG_FILE.name}: libs must be a non-empty mapping")

    ignore = data.get("ignore") or []
    if not isinstance(ignore, list) or not all(isinstance(item, str) for item in ignore):
        raise Die(f"{CONFIG_FILE.name}: ignore must be a list of strings")

    lib_entries = []
    for folder, url in libs.items():
        if not isinstance(folder, str) or not isinstance(url, str):
            raise Die(f"{CONFIG_FILE.name}: each lib must map a name to an svn url string")
        lib_entries.append((folder, url))

    return Config(
        name=name,
        curseforge_project_id=project_id,
        ignore=tuple(ignore),
        libs=tuple(lib_entries),
    )


@cache
def load_config() -> Config:
    try:
        text = CONFIG_FILE.read_text(encoding="utf-8")
    except OSError as error:
        raise Die(f"could not read {CONFIG_FILE.name}: {error}") from error
    return parse_config(text)
