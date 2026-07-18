"""Keep translations.yml honest and turn it into the Lua locale files.

  ./dev locales          reconcile translations.yml with the code, then report
  ./dev locales --check   report only, write nothing (for CI)
  ./dev prepare           generate Locales/*.lua from translations.yml

The first two live here. Generation is a step of prepare (packaging.py), which
calls generate() below.

Used keys are found by parsing the addon's Lua, not by matching text: a regex over
`L["..."]` misses `L['single']` and `L[ "spaced" ]`, mangles escaped quotes, and
matches inside comments and strings. The locale files themselves are generated
output now, so nothing here ever parses them; translations.yml is the source.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from luaparser import ast, astnodes  # type: ignore[ty:unresolved-import]

from common import Die
from config import Config, load_config
from toc import set_toc_locales, toc_locales
from translations import (
    DEFAULT_LOCALE,
    Message,
    dump_messages,
    parse_messages,
    read_messages,
    reconcile,
    sort_key,
    write_messages,
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Ace3 ships locale tables of its own and indexes them with expressions rather
# than literals, which is both noise and a parse hazard. Data.lua holds no strings
# at all and costs ~16s to parse against ~0.3s for everything else.
EXCLUDED_DIRS = frozenset({"Libs"})
EXCLUDED_FILES = frozenset({"Data.lua"})

# `%%` is an escaped percent and carries no argument, so it is not a specifier.
SPECIFIER = re.compile(r"%%|%[-+ #0]*\d*(?:\.\d+)?[diouxXeEfgGcsq]")
TOKEN = re.compile(r"\{(\w+)\}")

# Generated files say so, and point at the source, so nobody edits the output.
GENERATED_BANNER = (
    "-- Generated from src/translations.yml by `./dev prepare`. Do not edit by hand;\n"
    "-- edit that file instead.\n"
)

ERROR, WARNING = "error", "warning"


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


def relative_to(path: Path, root: Path) -> Path:
    """Shorten a path for display, leaving it alone if it is not under root."""
    try:
        return path.relative_to(root)
    except ValueError:
        return path


# --- Reading the strings the code actually uses -----------------------------


def lua_str(node: astnodes.Node) -> str | None:
    """luaparser hands back bytes with escapes already resolved."""
    if not isinstance(node, astnodes.String):
        return None
    return node.s.decode("utf-8") if isinstance(node.s, bytes) else node.s


def line_of(node: astnodes.Node) -> int | None:
    token = getattr(node, "_first_token", None)
    return token.line if token else None


def source_files(addon_dir: Path) -> list[Path]:
    """Every addon Lua file that might reference a string, locale files aside.

    The locale files are generated output where strings are defined rather than
    used, so counting them as usage would make every key look used and defeat the
    stale-key check.
    """
    locale_dir = addon_dir / "Locales"
    return sorted(
        p
        for p in addon_dir.rglob("*.lua")
        if not EXCLUDED_DIRS & set(p.relative_to(addon_dir).parts)
        and p.name not in EXCLUDED_FILES
        and locale_dir not in p.parents
    )


def find_usages(paths: list[Path]) -> tuple[dict[str, list[str]], list[Problem]]:
    """Every `L["key"]` read in the addon source, keyed to where it was seen."""
    used: dict[str, list[str]] = {}
    problems: list[Problem] = []

    for path in paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
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
                # A computed key is legal Lua, we just cannot verify it. Report and
                # carry on rather than crash the way p3lim's scanner does.
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


# --- Placeholders -----------------------------------------------------------


def specifiers(text: str) -> list[str]:
    """The printf specifiers in a string, in order, ignoring `%%`."""
    return sorted(m.group(0) for m in SPECIFIER.finditer(text) if m.group(0) != "%%")


def tokens(text: str) -> set[str]:
    return set(TOKEN.findall(text))


# --- Checks -----------------------------------------------------------------


def check_canonical(text: str, path: Path) -> list[Problem]:
    """The file must already be sorted and formatted the way locales writes it."""
    if text == dump_messages(parse_messages(text)):
        return []
    return [
        Problem(
            ERROR,
            path,
            None,
            "not in canonical form (sorting or formatting); run ./dev locales",
        )
    ]


def check_duplicates(messages: tuple[Message, ...], path: Path) -> list[Problem]:
    seen: set[str] = set()
    problems = []
    for message in messages:
        if message.key in seen:
            problems.append(
                Problem(ERROR, path, None, f"duplicate key {message.key!r}")
            )
        seen.add(message.key)
    return problems


def check_usage(
    messages: tuple[Message, ...], used: dict[str, list[str]], path: Path
) -> list[Problem]:
    """Every used key must be defined, and every defined key must be used."""
    defined = {message.key for message in messages}
    problems = []

    for key in sorted(set(used) - defined, key=sort_key):
        problems.append(
            Problem(
                ERROR,
                path,
                None,
                f"{key!r} is used at {', '.join(used[key])} but translations.yml "
                "does not define it",
            )
        )

    for key in sorted(defined - set(used), key=sort_key):
        problems.append(
            Problem(
                ERROR,
                path,
                None,
                f"{key!r} is defined but nothing uses it; ./dev locales will drop it",
            )
        )

    return problems


def check_empty(message: Message, path: Path) -> list[Problem]:
    """An empty translation is worse than none: it overrides English with nothing."""
    return [
        Problem(
            ERROR,
            path,
            None,
            f"{message.key!r} has an empty {locale} translation; remove it to fall "
            "back to English",
        )
        for locale, value in message.translations
        if value == ""
    ]


def check_context(message: Message, path: Path) -> list[Problem]:
    """A `Name|context` key must give its English out; `|context` is not a word."""
    if message.has_context and DEFAULT_LOCALE not in message.by_locale:
        return [
            Problem(
                ERROR,
                path,
                None,
                f"{message.key!r} has a context marker, so it needs an explicit "
                f"{DEFAULT_LOCALE} translation; without one players would see the marker",
            )
        ]
    return []


def check_placeholders(message: Message, path: Path) -> list[Problem]:
    """A translation must carry the same placeholders as the English it replaces.

    Dropping a `%s` loses an argument; turning `%s` into `%d` throws at runtime;
    misspelling `{expacIcon}` ships a broken tooltip that English never shows.
    """
    reference = message.english
    problems = []
    for locale, value in message.translations:
        if value == "":
            continue

        want, got = specifiers(reference), specifiers(value)
        if want != got:
            problems.append(
                Problem(
                    ERROR,
                    path,
                    None,
                    f"placeholder mismatch for {message.key!r} in {locale}: "
                    f"English has {want or 'none'}, this has {got or 'none'}",
                )
            )

        want_tokens, got_tokens = tokens(reference), tokens(value)
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
                    path,
                    None,
                    f"token mismatch for {message.key!r} in {locale}: {detail}",
                )
            )
    return problems


def check_toc_locales(config: Config, messages: tuple[Message, ...]) -> list[Problem]:
    """The TOC's generated file list must name exactly the locales in the source.

    They only diverge when a whole language is added or dropped and prepare has not
    run since, which would leave the new locale's file unloaded (or a dead entry).
    """
    try:
        toc_text = config.toc_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []

    current, expected = toc_locales(toc_text), locales_in(messages)
    if current == expected:
        return []
    return [
        Problem(
            ERROR,
            config.toc_path,
            None,
            f"the TOC loads locales {current}, but translations.yml implies "
            f"{expected}; run ./dev prepare",
        )
    ]


@dataclass(frozen=True)
class Analysis:
    problems: tuple[Problem, ...]
    messages: tuple[Message, ...]
    used: dict[str, list[str]]

    @property
    def errors(self) -> int:
        return sum(1 for p in self.problems if p.severity == ERROR)

    @property
    def warnings(self) -> int:
        return sum(1 for p in self.problems if p.severity == WARNING)


def analyse(config: Config) -> Analysis:
    """Read the source and the translations, run every check. Writes nothing."""
    problems: list[Problem] = []

    used, usage_problems = find_usages(source_files(config.source_dir))
    problems += usage_problems

    path = config.translations_path
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        text = ""

    try:
        messages = parse_messages(text)
    except Die as error:
        # A schema or YAML error: nothing further can be checked meaningfully.
        problems.append(Problem(ERROR, path, None, str(error)))
        return Analysis(tuple(problems), (), used)

    problems += check_canonical(text, path)
    problems += check_duplicates(messages, path)
    problems += check_usage(messages, used, path)
    problems += check_toc_locales(config, messages)
    for message in messages:
        problems += check_empty(message, path)
        problems += check_context(message, path)
        problems += check_placeholders(message, path)

    return Analysis(tuple(problems), messages, used)


def fix(config: Config) -> bool:
    """Reconcile translations.yml with the code and rewrite it. Returns changed."""
    used, _ = find_usages(source_files(config.source_dir))
    messages = read_messages(config.translations_path)
    reconciled = reconcile(messages, used.keys())

    text = dump_messages(reconciled)
    try:
        before = config.translations_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        before = ""

    if text == before:
        return False
    write_messages(config.translations_path, reconciled)
    return True


# --- Generating the Lua locale files ----------------------------------------


def lua_quote(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def header_for(locale: str, is_default: bool) -> str:
    """The AceLocale boilerplate at the top of a locale file.

    The `if not L then return end` guard is only correct because each locale is its
    own file: NewLocale returns nil for every locale but the player's, and a return
    at file scope ends the file. In a combined file it would swallow every locale
    after the first.
    """
    default_arg = ", true" if is_default else ""
    return (
        "local AddonName = ...\n"
        "\n"
        f'local L = LibStub("AceLocale-3.0"):NewLocale(AddonName, "{locale}"{default_arg})\n'
        "if not L then\n"
        "  return\n"
        "end\n"
    )


def locales_in(messages: tuple[Message, ...]) -> list[str]:
    """enUS first, then every other locale that has at least one real translation."""
    others = {
        locale
        for message in messages
        for locale, value in message.translations
        if value and locale != DEFAULT_LOCALE
    }
    return [DEFAULT_LOCALE, *sorted(others)]


def render_locale(messages: tuple[Message, ...], locale: str) -> str:
    is_default = locale == DEFAULT_LOCALE
    lines = []

    for message in sorted(messages, key=lambda m: sort_key(m.key)):
        if is_default:
            english = message.english
            if english == message.key:
                # `= true` is AceLocale's "the value is the key", the whole point
                # of the default locale.
                lines.append(f"L[{lua_quote(message.key)}] = true")
            else:
                lines.append(f"L[{lua_quote(message.key)}] = {lua_quote(english)}")
            continue

        value = message.by_locale.get(locale)
        if not value:
            continue
        lines.append(f"L[{lua_quote(message.key)}] = {lua_quote(value)}")

    return GENERATED_BANNER + "\n" + header_for(locale, is_default) + "\n" + "\n".join(lines) + "\n"


def generate(config: Config) -> list[Path]:
    """Write Locales/*.lua from translations.yml and sync the TOC's file list.

    The directory is treated as ours entirely: files for locales that no longer
    have translations are removed, so it always mirrors the source.
    """
    messages = read_messages(config.translations_path)
    ordered = locales_in(messages)

    locales_dir = config.locales_dir
    locales_dir.mkdir(parents=True, exist_ok=True)

    wanted = {f"{locale}.lua" for locale in ordered}
    for existing in locales_dir.glob("*.lua"):
        if existing.name not in wanted:
            existing.unlink()

    written = []
    for locale in ordered:
        path = locales_dir / f"{locale}.lua"
        path.write_text(render_locale(messages, locale), encoding="utf-8")
        written.append(path)

    toc_text = config.toc_path.read_text(encoding="utf-8")
    synced = set_toc_locales(toc_text, ordered)
    if synced != toc_text:
        config.toc_path.write_text(synced, encoding="utf-8")

    return written


# --- Command ----------------------------------------------------------------


def coverage(messages: tuple[Message, ...]) -> dict[str, int]:
    """How many keys each non-default locale translates, for the summary."""
    counts: dict[str, int] = {}
    for message in messages:
        for locale, value in message.translations:
            if value and locale != DEFAULT_LOCALE:
                counts[locale] = counts.get(locale, 0) + 1
    return counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dev locales",
        description="Reconcile translations.yml with the code, or just check it.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report only, write nothing, exit non-zero on error (for CI)",
    )
    args = parser.parse_args(argv)

    config = load_config()

    changed = False
    if not args.check:
        changed = fix(config)

    analysis = analyse(config)

    for problem in sorted(analysis.problems, key=lambda p: (str(p.path), p.line or 0, p.message)):
        print(problem.render())

    total = len(analysis.messages)
    counts = coverage(analysis.messages)
    print()
    print(f"{total} keys, {len(analysis.used)} used in source")
    for locale in sorted(counts):
        pct = (100 * counts[locale] // total) if total else 0
        print(f"  {locale}: {counts[locale]}/{total} translated ({pct}%)")

    if changed:
        print()
        print("rewrote translations.yml")

    print()
    print(f"{analysis.errors} error(s), {analysis.warnings} warning(s)")

    return 1 if analysis.errors else 0
