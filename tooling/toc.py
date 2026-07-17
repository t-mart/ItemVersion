"""Reading and writing the `## Field:` lines at the top of the TOC."""

from __future__ import annotations

from common import Die


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


def version_from_toc(text: str) -> str | None:
    return toc_field(text, "Version")


def require_version(text: str) -> str:
    """The TOC version, or a fatal error. Building a release without one is a bug."""
    version = version_from_toc(text)
    if version is None:
        raise Die("the TOC has no ## Version line")
    return version
