# /// script
# requires-python = ">=3.11"
# dependencies = ["luaparser>=3.2.1"]
# ///
"""Keep the locale files honest.

Usage:
  uv run scripts/locales.py            fix what can be fixed safely, then report
  uv run scripts/locales.py --check    report only, never write, exit 1 on error

--check is what CI runs. It makes no edits, so a pull request fails rather than
arrives with a surprise commit.

Strings are found by parsing Lua, not by matching text. A regex over `L["..."]`
misses `L['single']` and `L[ "spaced" ]`, mangles escaped quotes, and matches
inside comments and strings.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator

from luaparser import ast, astnodes  # type: ignore[ty:unresolved-import]

REPO_ROOT = Path(__file__).resolve().parent.parent
ADDON_DIRNAME = "ItemVersion"

# Ace3 ships locale tables of its own and indexes them with expressions rather
# than literals, which is both noise and a parse hazard. Data.lua holds no
# strings at all and costs ~16s to parse against ~0.3s for everything else.
EXCLUDED_DIRS = frozenset({"Libs"})
EXCLUDED_FILES = frozenset({"Data.lua"})

# `%%` is an escaped percent and carries no argument, so it is not a specifier.
SPECIFIER = re.compile(r"%%|%[-+ #0]*\d*(?:\.\d+)?[diouxXeEfgGcsq]")
TOKEN = re.compile(r"\{(\w+)\}")

ERROR, WARNING, INFO = "error", "warning", "info"


@dataclass(frozen=True)
class Problem:
    severity: str
    path: Path
    line: int | None
    message: str

    def render(self, root: Path = REPO_ROOT) -> str:
        where = str(relative_to(self.path, root))
        if self.line is not None:
            where = f"{where}:{self.line}"
        return f"{self.severity}: {where}: {self.message}"


@dataclass(frozen=True)
class Entry:
    """One `L["key"] = value` assignment."""

    key: str
    value: str | None  # None when the value is `true`, meaning "same as key"
    line: int

    @property
    def is_noop(self) -> bool:
        """True when this entry says nothing the enUS fallback would not say.

        `= true` is rewritten by AceLocale to the key itself, and a value that
        merely echoes the key is the same thing spelled out. In a non-default
        locale both are identical to having no entry at all.
        """
        return self.value is None or self.value == self.key


@dataclass(frozen=True)
class LocaleFile:
    path: Path
    locale: str
    is_default: bool
    entries: tuple[Entry, ...]
    header: str

    @property
    def by_key(self) -> dict[str, Entry]:
        return {e.key: e for e in self.entries}


def relative_to(path: Path, root: Path) -> Path:
    """Shorten a path for display, leaving it alone if it is not under root."""
    try:
        return path.relative_to(root)
    except ValueError:
        return path


def lua_str(node: astnodes.Node) -> str | None:
    """luaparser hands back bytes with escapes already resolved."""
    if not isinstance(node, astnodes.String):
        return None
    return node.s.decode("utf-8") if isinstance(node.s, bytes) else node.s


def line_of(node: astnodes.Node) -> int | None:
    token = getattr(node, "_first_token", None)
    return token.line if token else None


def parse(path: Path) -> astnodes.Chunk:
    return ast.parse(path.read_text(encoding="utf-8"))


def source_files(addon_dir: Path) -> list[Path]:
    """Every addon Lua file that might reference a string, locale files aside."""
    locale_dir = addon_dir / "Locales"
    return sorted(
        p
        for p in addon_dir.rglob("*.lua")
        if not EXCLUDED_DIRS & set(p.relative_to(addon_dir).parts)
        and p.name not in EXCLUDED_FILES
        and locale_dir not in p.parents
        and p.name != "Locales.lua"
    )


def locale_files(addon_dir: Path) -> list[Path]:
    locale_dir = addon_dir / "Locales"
    if not locale_dir.is_dir():
        return []
    return sorted(locale_dir.glob("*.lua"))


def find_usages(paths: list[Path]) -> tuple[dict[str, list[str]], list[Problem]]:
    """Every `L["key"]` read in the addon source, keyed to where it was seen."""
    used: dict[str, list[str]] = {}
    problems: list[Problem] = []

    for path in paths:
        try:
            tree = parse(path)
        except Exception as exc:  # luaparser raises a grab-bag of types
            problems.append(Problem(ERROR, path, None, f"could not parse: {exc}"))
            continue

        for node in ast.walk(tree):
            if not isinstance(node, astnodes.Index):
                continue
            if not (isinstance(node.value, astnodes.Name) and node.value.id == "L"):
                continue

            key = lua_str(node.idx)
            line = line_of(node.idx) or line_of(node)

            if key is None:
                # p3lim's scanner crashes here. Report and carry on: a computed
                # key is legal Lua, we just cannot verify it.
                problems.append(
                    Problem(
                        WARNING,
                        path,
                        line,
                        "L[...] indexed by an expression, cannot verify this key",
                    )
                )
                continue

            used.setdefault(key, []).append(f"{path.name}:{line}")

    return used, problems


def read_entries(tree: astnodes.Chunk) -> Iterator[Entry]:
    for node in ast.walk(tree):
        if not isinstance(node, astnodes.Assign):
            continue
        for target, value in zip(node.targets, node.values):
            if not isinstance(target, astnodes.Index):
                continue
            key = lua_str(target.idx)
            if key is None:
                continue

            is_true = isinstance(value, astnodes.TrueExpr)
            yield Entry(
                key=key,
                value=None if is_true else lua_str(value),
                line=line_of(target.idx) or 0,
            )


def read_locale(path: Path) -> LocaleFile | Problem:
    try:
        tree = parse(path)
    except Exception as exc:
        return Problem(ERROR, path, None, f"could not parse: {exc}")

    entries = tuple(read_entries(tree))

    # Everything above the first assignment is the file's own business: the
    # NewLocale call, the `if not L then return end` guard, comments. Fix mode
    # regenerates the entry list below it and leaves this alone.
    text = path.read_text(encoding="utf-8")
    first_line = min((e.line for e in entries), default=0)
    header = "".join(text.splitlines(keepends=True)[: max(first_line - 1, 0)])

    declared, is_default = declared_locale(tree)
    return LocaleFile(
        path=path,
        locale=declared or path.stem,
        is_default=is_default,
        entries=entries,
        header=header,
    )


def declared_locale(tree: astnodes.Chunk) -> tuple[str | None, bool]:
    """Read the locale out of the file's NewLocale call, mirroring AceLocale.

    Returns (locale, is_default). A file with no call at all, which is what a
    raw CurseForge export looks like, yields (None, False) and falls back to
    its filename.
    """
    for node in ast.walk(tree):
        # `x:NewLocale(...)` is an Invoke; a plain `f(...)` would be a Call.
        if not isinstance(node, astnodes.Invoke):
            continue
        if getattr(node.func, "id", None) != "NewLocale":
            continue
        args = node.args
        if len(args) < 2:
            continue
        locale = lua_str(args[1])
        is_default = len(args) >= 3 and isinstance(args[2], astnodes.TrueExpr)
        if locale:
            return locale, is_default
    return None, False


def specifiers(text: str) -> list[str]:
    """The printf specifiers in a string, in order, ignoring `%%`."""
    return sorted(m.group(0) for m in SPECIFIER.finditer(text) if m.group(0) != "%%")


def tokens(text: str) -> set[str]:
    return set(TOKEN.findall(text))


def check_placeholders(locale: LocaleFile, reference: set[str]) -> list[Problem]:
    """A translation must carry the same placeholders as the string it replaces.

    Dropping a `%s` silently loses an argument. Turning `%s` into `%d` throws at
    runtime. Misspelling `{expacIcon}` ships a broken default tooltip format to
    everyone in that locale, which is invisible in English.
    """
    problems = []
    for entry in locale.entries:
        if entry.value is None or entry.key not in reference:
            continue

        want, got = specifiers(entry.key), specifiers(entry.value)
        if want != got:
            problems.append(
                Problem(
                    ERROR,
                    locale.path,
                    entry.line,
                    f"placeholder mismatch for {entry.key!r}: "
                    f"enUS has {want or 'none'}, this has {got or 'none'}",
                )
            )

        want_tokens, got_tokens = tokens(entry.key), tokens(entry.value)
        if want_tokens != got_tokens:
            missing = sorted(want_tokens - got_tokens)
            extra = sorted(got_tokens - want_tokens)
            detail = ", ".join(
                part
                for part in (
                    f"missing {missing}" if missing else "",
                    f"unknown {extra}" if extra else "",
                )
                if part
            )
            problems.append(
                Problem(
                    ERROR,
                    locale.path,
                    entry.line,
                    f"token mismatch for {entry.key!r}: {detail}",
                )
            )
    return problems


def check_duplicates(locale: LocaleFile) -> list[Problem]:
    seen: dict[str, int] = {}
    problems = []
    for entry in locale.entries:
        if entry.key in seen:
            problems.append(
                Problem(
                    ERROR,
                    locale.path,
                    entry.line,
                    f"duplicate key {entry.key!r}, silently overwrites line {seen[entry.key]}",
                )
            )
        seen[entry.key] = entry.line
    return problems


def check_unknown_keys(locale: LocaleFile, reference: set[str]) -> list[Problem]:
    return [
        Problem(
            ERROR,
            locale.path,
            entry.line,
            f"key {entry.key!r} is not in enUS, so it is dead weight",
        )
        for entry in locale.entries
        if entry.key not in reference
    ]


def sort_key(key: str) -> tuple[str, str]:
    """Case-insensitive, with the raw key breaking ties so it is total."""
    return (key.lower(), key)


def check_sorted(locale: LocaleFile) -> list[Problem]:
    keys = [e.key for e in locale.entries]
    if keys == sorted(keys, key=sort_key):
        return []
    return [
        Problem(
            WARNING,
            locale.path,
            None,
            "keys are not sorted, which makes diffs and merges noisy",
        )
    ]


def render(locale: LocaleFile, reference: Iterable[str]) -> str:
    """Canonical text for a locale file: header verbatim, entries regenerated.

    Untranslated keys become commented stubs so a translator opening the file
    sees exactly what is left. A stub does not parse as an assignment, so the
    next run treats it as missing again and reproduces it. That makes this
    idempotent.
    """
    translated = {e.key: e for e in locale.entries if not e.is_noop}
    lines = []

    for key in sorted(reference, key=sort_key):
        entry = translated.get(key)

        if locale.is_default:
            # enUS is the reference. The convention is `= true`, meaning the
            # value is the key.
            lines.append(f"L[{lua_quote(key)}] = true")
            continue

        if entry is None:
            lines.append(f"-- L[{lua_quote(key)}] = {lua_quote('')}")
            continue

        lines.append(f"L[{lua_quote(key)}] = {lua_quote(entry.value or key)}")

    return locale.header.rstrip("\n") + "\n" + "\n".join(lines) + "\n"


def lua_quote(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def coverage(locale: LocaleFile, reference: set[str]) -> tuple[int, int]:
    translated = {e.key for e in locale.entries if not e.is_noop and e.key in reference}
    return len(translated), len(reference)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check, and optionally fix, the addon's locale files."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report only, write nothing, exit non-zero on error (for CI)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="repo root to work on, for testing against a scratch tree",
    )
    args = parser.parse_args()

    root: Path = args.root.resolve()
    addon_dir = root / ADDON_DIRNAME

    problems: list[Problem] = []

    used, usage_problems = find_usages(source_files(addon_dir))
    problems += usage_problems

    locales: list[LocaleFile] = []
    for path in locale_files(addon_dir):
        result = read_locale(path)
        if isinstance(result, Problem):
            problems.append(result)
            continue
        locales.append(result)

    default = next((loc for loc in locales if loc.is_default), None)
    if default is None:
        # Transitional: enUS still lives in the single Locales.lua alongside the
        # @localization@ blocks. Once that file is split up, the isDefault call
        # above finds enUS.lua and this goes away.
        legacy = addon_dir / "Locales.lua"
        result = read_locale(legacy) if legacy.exists() else None
        if isinstance(result, LocaleFile) and result.entries:
            default = result

    if default is None:
        print("error: found no default (enUS) locale to check against", file=sys.stderr)
        return 1

    reference = default.by_key
    reference_keys = set(reference)

    # The check that prevents a shipped bug: a missing enUS entry makes
    # AceLocale call geterrorhandler(), which is an error popup for the player.
    for key in sorted(set(used) - reference_keys, key=sort_key):
        problems.append(
            Problem(
                ERROR,
                default.path,
                None,
                f"{key!r} is used at {', '.join(used[key])} but enUS does not define it",
            )
        )

    for key in sorted(reference_keys - set(used), key=sort_key):
        problems.append(
            Problem(
                WARNING,
                default.path,
                reference[key].line,
                f"{key!r} is defined but never used",
            )
        )

    for locale in locales:
        problems += check_duplicates(locale)
        problems += check_unknown_keys(locale, reference_keys)
        problems += check_placeholders(locale, reference_keys)
        problems += check_sorted(locale)

    written = []
    if not args.check:
        for locale in locales:
            text = render(locale, reference_keys)
            if text != locale.path.read_text(encoding="utf-8"):
                locale.path.write_text(text, encoding="utf-8")
                written.append(locale.path)

    for problem in sorted(problems, key=lambda p: (str(p.path), p.line or 0)):
        print(problem.render(root))

    print()
    print(f"enUS: {len(reference_keys)} keys, {len(used)} used in source")
    for locale in sorted(locales, key=lambda loc: loc.locale):
        if locale.is_default:
            continue
        done, total = coverage(locale, reference_keys)
        pct = (100 * done // total) if total else 0
        print(f"  {locale.locale}: {done}/{total} translated ({pct}%)")

    if written:
        print()
        for path in written:
            print(f"rewrote {relative_to(path, root)}")

    errors = sum(1 for p in problems if p.severity == ERROR)
    warnings = sum(1 for p in problems if p.severity == WARNING)
    print()
    print(f"{errors} error(s), {warnings} warning(s)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
