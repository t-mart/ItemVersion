"""Reading and writing the `## Field:` lines at the top of the TOC.

Also owns the list of `Locales\\*.lua` files further down, which the locale tool
regenerates from translations.yml so adding a language never touches the TOC by
hand.
"""

from __future__ import annotations

import fnmatch
import re

from common import Die

# A file-list entry loading a locale, as `Locales\enUS.lua`. Either slash, since
# WoW accepts both and a repo might have been written with forward slashes.
LOCALE_LINE = re.compile(r"^Locales[\\/].+\.lua\s*$")


def _references_a_devonly_file(line: str, patterns: tuple[str, ...]) -> bool:
    """True when a TOC file-list line points at a dev-only path.

    Matches the referenced path against each glob, both as a full relative path and
    by basename, with slashes normalized. Comment (`##`) and blank lines carry no
    file reference, so they never match.
    """
    reference = line.strip()
    if not reference or reference.startswith("#"):
        return False

    normalized = reference.replace("\\", "/")
    basename = normalized.rsplit("/", 1)[-1]
    for pattern in patterns:
        glob = pattern.replace("\\", "/")
        if fnmatch.fnmatch(normalized, glob) or fnmatch.fnmatch(basename, glob):
            return True
    return False


def strip_files(text: str, patterns: tuple[str, ...]) -> str:
    """The TOC with any file-list line referencing a dev-only path removed.

    So a packaged TOC never names a file the build left out. Line endings and every
    other line are preserved.
    """
    if not patterns:
        return text

    lines = text.splitlines(keepends=True)
    kept = [line for line in lines if not _references_a_devonly_file(line, patterns)]
    return "".join(kept)


def toc_field(text: str, field: str) -> str | None:
    """The value of a `## Field:` line, or None if the TOC has no such line."""
    prefix = f"## {field}:"

    for line in text.splitlines():
        if line.startswith(prefix):
            return line.removeprefix(prefix).strip()

    return None


def set_toc_field(text: str, field: str, value: str) -> str:
    """The TOC with one `## Field:` line rewritten. Raises if it is not there."""
    prefix = f"## {field}:"
    lines = text.splitlines(keepends=True)

    for index, line in enumerate(lines):
        if line.startswith(prefix):
            ending = "\n" if line.endswith("\n") else ""
            lines[index] = f"{prefix} {value}{ending}"
            return "".join(lines)

    raise Die(f"no '{prefix}' line to update")


def toc_locales(text: str) -> list[str]:
    """The locale codes the TOC's file list loads, in order, e.g. ['enUS', 'deDE']."""
    return [
        re.split(r"[\\/]", line.strip())[-1].removesuffix(".lua")
        for line in text.splitlines()
        if LOCALE_LINE.match(line)
    ]


def set_toc_locales(text: str, locales: list[str]) -> str:
    """The TOC with its `Locales\\*.lua` block rewritten to these locales, in order.

    Replaces the run of locale-file lines in place, leaving everything around it
    alone. Raises if there is no such block, or if the lines are not contiguous,
    since either means the TOC is not shaped the way this expects.
    """
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()

    hits = [index for index, line in enumerate(lines) if LOCALE_LINE.match(line)]
    if not hits:
        raise Die("the TOC has no Locales file block to update")
    first, last = hits[0], hits[-1]
    if hits != list(range(first, last + 1)):
        raise Die("the TOC's Locales lines are not contiguous")

    block = [f"Locales\\{locale}.lua" for locale in locales]
    rebuilt = lines[:first] + block + lines[last + 1 :]

    trailing = newline if text.endswith("\n") else ""
    return newline.join(rebuilt) + trailing


def version_from_toc(text: str) -> str | None:
    return toc_field(text, "Version")


def require_version(text: str) -> str:
    """The TOC version, or a fatal error. Building a release without one is a bug."""
    version = version_from_toc(text)
    if version is None:
        raise Die("the TOC has no ## Version line")
    return version
