"""Validating YAML config against the JSON schemas under schemas/.

The schema files are the single source of truth for the shape of wowaddon.yml and
translations.yml. Editors read them through the `# yaml-language-server: $schema`
comment at the top of each file, and check runs them through jsonschema here, so
the two can never drift.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path

import jsonschema  # type: ignore[ty:unresolved-import]

from common import Die

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


@cache
def load_schema(name: str) -> dict:
    path = SCHEMA_DIR / f"{name}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _where(error: jsonschema.ValidationError) -> str:
    """The path to the offending value, as `a/b/0`, or `root` at the top."""
    return "/".join(str(part) for part in error.absolute_path) or "root"


def validate(data: object, schema_name: str, source: str) -> None:
    """Check data against a named schema, raising Die on the first problem.

    jsonschema's own message is kept, since it names the failing keyword, with the
    file and location prefixed so the reader knows what to open.
    """
    schema = load_schema(schema_name)
    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as error:
        raise Die(f"{source} at {_where(error)}: {error.message}") from error
