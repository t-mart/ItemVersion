"""Tests for the lint/format/watch commands."""

from __future__ import annotations

from pathlib import Path

import common
import quality

SOURCE = common.REPO_ROOT / "src" / "ItemVersion"
LIBS = SOURCE / "Libs"
LOCALES = SOURCE / "Locales"


class TestIsWatched:
    def test_addon_sources_are_watched(self):
        for name in ("Init.lua", "ItemVersion.toc", "Libs.xml"):
            assert quality.is_watched(str(SOURCE / name), LIBS, LOCALES), name

    def test_nested_sources_are_watched(self):
        assert quality.is_watched(str(SOURCE / "Widgets" / "Slider.lua"), LIBS, LOCALES)

    def test_other_extensions_are_not(self):
        for name in ("icon.tga", "notes.md", "ItemVersion.lua.bak", "Init"):
            assert not quality.is_watched(str(SOURCE / name), LIBS, LOCALES), name

    def test_vendored_libs_are_not_watched(self):
        # The reason the filter exists: Ace3 is large, never edited, and selene
        # skips it anyway.
        assert not quality.is_watched(
            str(LIBS / "AceAddon-3.0" / "AceAddon-3.0.lua"), LIBS, LOCALES
        )

    def test_the_libs_dir_itself_is_not_watched(self):
        assert not quality.is_watched(str(LIBS), LIBS, LOCALES)

    def test_generated_locales_are_not_watched(self):
        # They are regenerated from translations.yml, so watching them would loop.
        assert not quality.is_watched(str(LOCALES / "deDE.lua"), LIBS, LOCALES)
        assert not quality.is_watched(str(LOCALES), LIBS, LOCALES)

    def test_a_lua_file_merely_named_libs_is_watched(self):
        # Libs.xml and a Libs.lua live in the addon root and are ours.
        assert quality.is_watched(str(SOURCE / "Libs.lua"), LIBS, LOCALES)


class TestSyncGenerated:
    """What the watch loop does with a batch of changed files."""

    TRANSLATIONS = Path("/repo/src/translations.yml")
    CONFIG = Path("/repo/wowaddon.yml")

    def _spies(self, monkeypatch):
        # Stub only the two side effects. The real (cached) load_config is left in
        # place, so sync_generated's cache_clear on a wowaddon.yml change is real.
        calls = []
        monkeypatch.setattr(quality.locales, "generate", lambda config: calls.append("generate"))
        monkeypatch.setattr(quality.packaging, "ensure_libs", lambda config: calls.append("libs"))
        return calls

    def test_a_translations_change_regenerates_locales(self, monkeypatch):
        calls = self._spies(monkeypatch)
        quality.sync_generated(None, {self.TRANSLATIONS}, self.TRANSLATIONS, self.CONFIG)
        assert calls == ["generate"]

    def test_a_wowaddon_change_fetches_libs(self, monkeypatch):
        calls = self._spies(monkeypatch)
        quality.sync_generated(None, {self.CONFIG}, self.TRANSLATIONS, self.CONFIG)
        assert calls == ["libs"]

    def test_an_ordinary_source_change_does_neither(self, monkeypatch):
        calls = self._spies(monkeypatch)
        quality.sync_generated(None, {Path("/repo/src/ItemVersion/Init.lua")}, self.TRANSLATIONS, self.CONFIG)
        assert calls == []

    def test_a_malformed_translations_file_does_not_escape(self, monkeypatch):
        def boom(config):
            raise common.Die("bad yaml")

        monkeypatch.setattr(quality.locales, "generate", boom)
        # No exception: the watch loop must survive a broken save.
        quality.sync_generated(None, {self.TRANSLATIONS}, self.TRANSLATIONS, self.CONFIG)


class TestDescribe:
    def test_names_the_change_and_a_relative_path(self):
        changes = {(quality.Change.modified, str(SOURCE / "Init.lua"))}
        assert quality.describe(changes) == ["modified src/ItemVersion/Init.lua"]

    def test_is_sorted_and_lists_every_change(self):
        # A list, not a set: set iteration order is arbitrary, so a set can land
        # already sorted and let a missing sort() pass unnoticed. This order is
        # reverse-sorted, so it can only pass if the sort really happens.
        changes = [
            (quality.Change.modified, str(SOURCE / "Zed.lua")),
            (quality.Change.deleted, str(SOURCE / "Mid.lua")),
            (quality.Change.added, str(SOURCE / "Init.lua")),
        ]
        assert quality.describe(changes) == [
            "added src/ItemVersion/Init.lua",
            "deleted src/ItemVersion/Mid.lua",
            "modified src/ItemVersion/Zed.lua",
        ]
