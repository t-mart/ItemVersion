"""The TOC's Interface line, straight from Blizzard's version endpoints."""

from __future__ import annotations

import sys
import urllib.request
from typing import Iterable

from common import TOC_PATH, Die, relative
from toc import set_toc_field, toc_field

# Despite the us. hostname, one response covers every region.
# See https://wowdev.wiki/TACT#HTTP_URLs
VERSIONS_URL = "http://us.patch.battle.net:1119/{product}/versions"

# The products the addon supports, in the order the TOC lists their interfaces.
WOW_PRODUCTS = ("wow", "wow_classic", "wow_anniversary", "wow_classic_era")

REGION = "us"


def fetch_text(url: str, timeout: int = 30) -> str:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except OSError as error:
        raise Die(f"could not fetch {url}: {error}") from error


def parse_versions(text: str) -> list[dict[str, str]]:
    """The rows of a versions response, keyed by column name.

    The body is a pipe-separated table: a header naming each column as
    `Name!TYPE:size`, a `## seqn = N` line, then one row per region. Only the
    names matter here, so the declared types are dropped.
    """
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise Die("versions response was empty")

    columns = [field.split("!")[0] for field in lines[0].split("|")]

    rows = []
    for line in lines[1:]:
        # `## seqn = N` and anything else Blizzard adds later.
        if line.startswith("#"):
            continue

        values = line.split("|")
        if len(values) != len(columns):
            raise Die(f"versions row has {len(values)} fields, expected {len(columns)}")

        rows.append(dict(zip(columns, values)))

    if not rows:
        raise Die("versions response had no rows")

    return rows


def interface_version(versions_name: str) -> str:
    """`12.0.7.68453` -> `120007`: major, then two-digit minor and patch."""
    parts = versions_name.split(".")
    if len(parts) != 4:
        raise Die(f"cannot read a version out of {versions_name!r}")

    major, minor, patch, _build = parts
    try:
        return f"{int(major)}{int(minor):02d}{int(patch):02d}"
    except ValueError as error:
        raise Die(f"cannot read a version out of {versions_name!r}") from error


def interface_for(product: str, region: str = REGION) -> str:
    rows = parse_versions(fetch_text(VERSIONS_URL.format(product=product)))

    for row in rows:
        if row.get("Region") != region:
            continue

        name = row.get("VersionsName")
        if not name:
            raise Die(f"{product}: the {region} row has no VersionsName")

        return interface_version(name)

    raise Die(f"{product}: no {region} row in the versions response")


def current_interfaces(
    products: Iterable[str] = WOW_PRODUCTS, region: str = REGION
) -> str:
    """What the TOC's Interface line should say, straight from Blizzard."""
    return ", ".join(interface_for(product, region) for product in products)


def cmd_interfaces(dry_run: bool = False) -> int:
    interfaces = current_interfaces()

    text = TOC_PATH.read_text(encoding="utf-8")
    listed = toc_field(text, "Interface")
    updated = set_toc_field(text, "Interface", interfaces)

    if updated == text:
        print(f"{relative(TOC_PATH)} already lists {interfaces}", file=sys.stderr)
    elif dry_run:
        print(
            f"would update {relative(TOC_PATH)}: {listed} -> {interfaces}",
            file=sys.stderr,
        )
    else:
        TOC_PATH.write_text(updated, encoding="utf-8")
        print(
            f"updated {relative(TOC_PATH)}: {listed} -> {interfaces}", file=sys.stderr
        )

    # Notes above go to stderr so that stdout is just the value, which the release
    # workflow puts in its commit message.
    print(interfaces)
    return 0
