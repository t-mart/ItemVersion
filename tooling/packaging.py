"""Fetching the embedded libraries and building the addon zip.

Both of these used to shell out to the BigWigs packager. They are plain Python
now: libraries are svn exports into the addon's Libs dir, and a build is a copy of
the source directory with the build date stamped into the TOC, zipped up. The zip
holds a single top-level folder named after the addon, which is what WoW expects.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import locales
from common import REPO_ROOT, Die, relative, report, require_tool, run
from config import Config, load_config
from toc import require_version, strip_files

BUILD_ROOT = REPO_ROOT / "dist"

# Written into the built TOC, never the source. WoW ignores unknown ## fields, so
# this just rides along as a record of when the zip was made.
BUILD_DATE_FIELD = "X-Build-Date-Time"


def _fetch_lib(libs_dir: Path, folder: str, url: str) -> None:
    libs_dir.mkdir(parents=True, exist_ok=True)
    # export, not checkout: we want the files, not a working copy with .svn dirs
    # that would then have to be kept out of the build.
    if run(["svn", "export", "--quiet", url, str(libs_dir / folder)]) != 0:
        raise Die(f"could not export {folder} from {url}")


def _missing_libs(config: Config) -> list[tuple[str, str]]:
    return [(folder, url) for folder, url in config.libs if not (config.libs_dir / folder).is_dir()]


def ensure_libs(config: Config) -> None:
    """Fetch any libraries a build needs but that are not on disk yet."""
    missing = _missing_libs(config)
    if not missing:
        return
    require_tool("svn")
    for folder, url in missing:
        _fetch_lib(config.libs_dir, folder, url)
        report(folder, "fetched")


def cmd_prepare_src() -> int:
    """Populate the addon's generated bits: the embedded libs and the locale files.

    Both are gitignored output that build and install need but do not commit. Libs
    are fetched only when missing; the locale files are regenerated every run, so
    they always match translations.yml.
    """
    config = load_config()
    require_tool("svn")

    for folder, url in config.libs:
        if (config.libs_dir / folder).is_dir():
            report(folder, "present")
            continue
        _fetch_lib(config.libs_dir, folder, url)
        report(folder, "fetched")

    written = locales.generate(config)
    report("locales", f"generated {len(written)} file(s) in {relative(config.locales_dir)}")

    print(f"{config.name} is ready. Run build or install next.")
    return 0


def stamp_build_date(text: str, when: datetime) -> str:
    """Add the build-date field to a TOC's header block.

    The header is the run of ## lines at the top; the new field goes at its end,
    just before the file list. The TOC's own line ending is preserved.
    """
    newline = "\r\n" if "\r\n" in text else "\n"
    stamp = when.strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = f"## {BUILD_DATE_FIELD}: {stamp}{newline}"

    lines = text.splitlines(keepends=True)
    insert_at = 0
    for index, line in enumerate(lines):
        if line.lstrip().startswith("##"):
            insert_at = index + 1
        else:
            break

    lines.insert(insert_at, entry)
    return "".join(lines)


def _zip_dir(source_dir: Path, archive: Path, arc_root: str) -> None:
    with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                zip_file.write(path, Path(arc_root) / path.relative_to(source_dir))


def cmd_build() -> int:
    config = load_config()
    ensure_libs(config)
    locales.generate(config)

    version = require_version(config.toc_path.read_text(encoding="utf-8"))
    staged = BUILD_ROOT / config.name

    if staged.exists():
        shutil.rmtree(staged)
    staged.parent.mkdir(parents=True, exist_ok=True)

    ignore = shutil.ignore_patterns(*config.dev_only) if config.dev_only else None
    shutil.copytree(config.source_dir, staged, ignore=ignore)

    staged_toc = staged / f"{config.name}.toc"
    toc_text = strip_files(staged_toc.read_text(encoding="utf-8"), config.dev_only)
    toc_text = stamp_build_date(toc_text, datetime.now(timezone.utc))
    staged_toc.write_text(toc_text, encoding="utf-8")

    archive = BUILD_ROOT / f"{config.name}-{version}.zip"
    _zip_dir(staged, archive, config.name)

    print(f"built {relative(archive)}")
    return 0


def cmd_clean() -> int:
    config = load_config()
    # Everything generated: the build output and both prepared trees.
    for path in (BUILD_ROOT, config.libs_dir, config.locales_dir):
        if path.is_dir():
            shutil.rmtree(path)
            print(f"removed {relative(path)}")

    return 0
