"""Bumping the calver version, which lives only in the TOC.

The version string is the single source of truth in the addon's TOC. This turns a
format like `{YYYY}.{0W}.{N}` into a concrete version and reads an existing one
back apart, so a bump can tell whether the calendar prefix moved (reset the serial
to 0) or held (increment it).

Week numbering is true ISO 8601 (Python's isocalendar), paired with the ISO
week-year for {YYYY} so the year and week always agree, even across a January
boundary. The trailing {N} is a 0-based serial: releases within one ISO week are
.0, .1, .2 and so on. To switch the whole project to Monday-first %W weeks
instead, change the two functions below; nothing else assumes the scheme.

This does no git: no commit, no tag, no push. The release workflow owns that.
"""

from __future__ import annotations

import re
import sys
from datetime import date
from typing import Callable

from common import REPO_ROOT, Die, relative
from config import load_config

# The serial part: 0-based, resets to 0 when the calendar prefix changes.
SERIAL_TOKEN = "{N}"


def _iso_week_year(on: date) -> str:
    return f"{on.isocalendar().year:04d}"


def _iso_week(on: date) -> str:
    return f"{on.isocalendar().week:02d}"


# Each calendar token: how to render it from a date, and the regex that matches it
# when reading a version back apart.
DATE_TOKENS: dict[str, tuple[Callable[[date], str], str]] = {
    "{YYYY}": (_iso_week_year, r"\d{4}"),
    "{0W}": (_iso_week, r"\d{2}"),
}

# Any {token} in a format string. Literals are everything between them.
_TOKEN = re.compile(r"\{[^{}]*\}")


def _known_tokens() -> str:
    return ", ".join([*DATE_TOKENS, SERIAL_TOKEN])


def render(fmt: str, on: date, serial: int) -> str:
    """The version this format produces on a given date with a given serial."""

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        if token == SERIAL_TOKEN:
            return str(serial)
        if token in DATE_TOKENS:
            return DATE_TOKENS[token][0](on)
        raise Die(f"version format {fmt!r} has unknown token {token}; known: {_known_tokens()}")

    return _TOKEN.sub(replace, fmt)


def _compile(fmt: str) -> tuple[re.Pattern[str], tuple[tuple[str, str], ...]]:
    """A regex matching versions of this format, plus its (group name, token) pairs.

    Date tokens become named digit groups and {N} becomes the `serial` group, with
    the literal text between them escaped. Validates the format on the way: an
    unknown token, a missing serial, or a repeated serial is a fatal error.
    """
    parts: list[str] = []
    date_names: list[tuple[str, str]] = []
    serial_seen = False
    position = 0

    for index, match in enumerate(_TOKEN.finditer(fmt)):
        parts.append(re.escape(fmt[position : match.start()]))
        token = match.group(0)

        if token == SERIAL_TOKEN:
            if serial_seen:
                raise Die(f"version format {fmt!r} has more than one {SERIAL_TOKEN}")
            serial_seen = True
            parts.append(r"(?P<serial>\d+)")
        elif token in DATE_TOKENS:
            name = f"t{index}"
            date_names.append((name, token))
            parts.append(f"(?P<{name}>{DATE_TOKENS[token][1]})")
        else:
            raise Die(f"version format {fmt!r} has unknown token {token}; known: {_known_tokens()}")

        position = match.end()

    parts.append(re.escape(fmt[position:]))

    if not serial_seen:
        raise Die(f"version format {fmt!r} must contain the serial token {SERIAL_TOKEN}")

    return re.compile("^" + "".join(parts) + "$"), tuple(date_names)


def next_version(fmt: str, current: str, on: date) -> str:
    """The version that follows `current` when bumping on a given date.

    The serial resets to 0 when the calendar prefix moves and increments by 1 when
    it holds. Raises if the format is malformed or `current` does not fit it.
    """
    regex, date_names = _compile(fmt)

    match = regex.match(current)
    if match is None:
        raise Die(f"current version {current!r} does not match format {fmt!r}")

    held = all(match.group(name) == DATE_TOKENS[token][0](on) for name, token in date_names)
    serial = int(match.group("serial")) + 1 if held else 0

    return render(fmt, on, serial)


def find_version(text: str, pattern: str) -> tuple[str, tuple[int, int]]:
    """The version substring the pattern locates, and its span in `text`.

    The pattern must match exactly once and expose the version through a `version`
    named group, or its first group. The span lets a bump replace just that
    substring and leave the rest of the file untouched.
    """
    try:
        regex = re.compile(pattern)
    except re.error as error:
        raise Die(f"version pattern is not valid regex: {error}") from error

    matches = list(regex.finditer(text))
    if not matches:
        raise Die(f"version pattern {pattern!r} matched nothing")
    if len(matches) > 1:
        raise Die(f"version pattern {pattern!r} matched {len(matches)} times, expected 1")

    match = matches[0]
    if "version" in match.groupdict():
        group: str | int = "version"
    elif regex.groups >= 1:
        group = 1
    else:
        raise Die(f"version pattern {pattern!r} needs a capture group for the version")

    return match.group(group), match.span(group)


def cmd_bump_calver(dry_run: bool = False) -> int:
    version_config = load_config().require_version_config
    path = REPO_ROOT / version_config.file
    text = path.read_text(encoding="utf-8")

    current, span = find_version(text, version_config.pattern)
    new = next_version(version_config.format, current, date.today())

    if dry_run:
        print(f"would bump {relative(path)}: {current} -> {new}", file=sys.stderr)
    else:
        path.write_text(text[: span[0]] + new + text[span[1] :], encoding="utf-8")
        print(f"bumped {relative(path)}: {current} -> {new}", file=sys.stderr)

    # Notes go to stderr so stdout is just the new version, which the release
    # workflow captures for its commit and tag.
    print(new)
    return 0
