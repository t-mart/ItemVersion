"""Tests for fetching the item database from item-version-scrape."""

from __future__ import annotations

import pytest  # type: ignore[ty:unresolved-import]

import common
import data
from config import Config

CONFIG = Config(
    name="ItemVersion",
    curseforge_project_id=433258,
    ignore=(),
    libs=(),
)


class TestGetData:
    def test_downloads_the_latest_asset_into_the_source_dir(self, monkeypatch, capsys):
        calls = []
        monkeypatch.setattr(data, "require_tool", lambda name: name)
        monkeypatch.setattr(data, "load_config", lambda: CONFIG)
        monkeypatch.setattr(data, "run", lambda command: calls.append(command) or 0)

        assert data.cmd_get_data() == 0

        command = calls[0]
        assert command[:3] == ["gh", "release", "download"]
        # No positional tag argument, so gh takes the latest release.
        assert command[3].startswith("--")
        assert "--repo" in command and data.DATA_REPO in command
        assert "--pattern" in command and data.DATA_ASSET in command
        assert "--clobber" in command
        # It lands in the addon source under the name the addon loads.
        assert str(CONFIG.source_dir / data.OUTPUT_NAME) in command

    def test_a_failed_download_dies(self, monkeypatch):
        monkeypatch.setattr(data, "require_tool", lambda name: name)
        monkeypatch.setattr(data, "load_config", lambda: CONFIG)
        monkeypatch.setattr(data, "run", lambda command: 1)

        with pytest.raises(common.Die, match="download failed"):
            data.cmd_get_data()

    def test_a_missing_gh_dies(self, monkeypatch):
        def missing(name):
            raise common.Die(f"{name} is not installed.")

        monkeypatch.setattr(data, "require_tool", missing)

        with pytest.raises(common.Die, match="not installed"):
            data.cmd_get_data()
