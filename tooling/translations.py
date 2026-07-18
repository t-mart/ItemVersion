"""The translation source: src/translations.yml, read, validated and written.

Each entry is one player-facing string: the key looked up in code as L["key"], an
optional description for translators, and a translation per locale. This module
owns the file's shape and its on-disk form. locales.py turns it into the generated
Lua locale files and keeps it reconciled with what the code actually uses.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml  # type: ignore[ty:unresolved-import]

import schema

# Kept at the top of the file so editors validate it against the schema as you
# type. dump re-emits it, since safe_dump would otherwise drop every comment.
SCHEMA_COMMENT = "# yaml-language-server: $schema=../tooling/schemas/translations.schema.json"

# The fallback locale. A key with no enUS translation shows its own text, which is
# how AceLocale spells an already-English string.
DEFAULT_LOCALE = "enUS"

# Separates a key from the role it plays, as in `Legion|canon` and `Legion|short`.
# Lets one English word carry two meanings other languages may tell apart. Never
# shown to a player, so such a key must give its English out explicitly.
CONTEXT_MARKER = "|"


def sort_key(key: str) -> tuple[str, str]:
    """Case-insensitive, with the raw key breaking ties so the order is total."""
    return (key.lower(), key)


@dataclass(frozen=True)
class Message:
    """One player-facing string and every translation of it."""

    key: str
    description: str | None
    translations: tuple[tuple[str, str], ...]  # (locale, text), sorted by locale

    @property
    def by_locale(self) -> dict[str, str]:
        return dict(self.translations)

    @property
    def english(self) -> str:
        """What enUS shows: an explicit enUS translation, else the key itself."""
        return self.by_locale.get(DEFAULT_LOCALE) or self.key

    @property
    def has_context(self) -> bool:
        return CONTEXT_MARKER in self.key


def parse_messages(text: str) -> tuple[Message, ...]:
    """Read the whole file, validate its shape, and return it sorted by key.

    Duplicate keys and empty values are left in place for the checker to report;
    this only guarantees the structure the schema describes.
    """
    data = yaml.safe_load(text) or []
    schema.validate(data, "translations", "translations.yml")

    messages = tuple(
        Message(
            key=item["key"],
            description=item.get("description"),
            translations=tuple(sorted(item.get("translations", {}).items())),
        )
        for item in data
    )
    return tuple(sorted(messages, key=lambda m: sort_key(m.key)))


def dump_messages(messages: Iterable[Message]) -> str:
    """The canonical text of the file: schema comment, then entries sorted by key.

    width is left huge so a long translation stays on one line, which keeps diffs
    readable when a single string changes.
    """
    items: list[dict] = []
    for message in sorted(messages, key=lambda m: sort_key(m.key)):
        entry: dict = {"key": message.key}
        if message.description:
            entry["description"] = message.description
        if message.translations:
            entry["translations"] = dict(message.translations)
        items.append(entry)

    body = yaml.safe_dump(
        items,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
        width=4096,
    )
    return f"{SCHEMA_COMMENT}\n{body}"


def read_messages(path: Path) -> tuple[Message, ...]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ()
    return parse_messages(text)


def write_messages(path: Path, messages: Iterable[Message]) -> None:
    path.write_text(dump_messages(messages), encoding="utf-8")


def reconcile(messages: Iterable[Message], used_keys: Iterable[str]) -> tuple[Message, ...]:
    """Keep entries for used keys, stub new ones, drop keys nothing references.

    Descriptions and translations of surviving keys are carried through untouched.
    A key the code uses but the file lacks becomes an empty entry, ready to fill in.
    """
    by_key = {message.key: message for message in messages}
    result = tuple(
        by_key.get(key, Message(key=key, description=None, translations=()))
        for key in set(used_keys)
    )
    return tuple(sorted(result, key=lambda m: sort_key(m.key)))
