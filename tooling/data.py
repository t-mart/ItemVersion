"""Fetching the generated item database from item-version-scrape.

ItemData.lua is produced by a separate project, t-mart/item-version-scrape, and
published as a release asset there. This pulls the latest one down into the addon
source so a developer can refresh their local copy without running a scrape, using gh
the same way the refresh-data workflow does.
"""

from __future__ import annotations

from common import Die, relative, require_tool, run
from config import load_config

# The generator lives in its own repo and publishes the data as a release asset.
DATA_REPO = "t-mart/item-version-scrape"
DATA_ASSET = "ItemVersionData.lua"
# The name the addon loads it under (see the TOC).
OUTPUT_NAME = "ItemData.lua"


def cmd_get_item_data() -> int:
    require_tool("gh")

    destination = load_config().source_dir / OUTPUT_NAME

    # No tag downloads the latest release. --clobber so the refresh overwrites the
    # copy already sitting there.
    failed = run(
        [
            "gh",
            "release",
            "download",
            "--repo",
            DATA_REPO,
            "--pattern",
            DATA_ASSET,
            "--output",
            str(destination),
            "--clobber",
        ]
    )
    if failed:
        raise Die("gh release download failed")

    print(f"  downloaded {DATA_ASSET} to {relative(destination)}")
    return 0
