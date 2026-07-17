"""Tests for the lint/format/watch commands."""

from __future__ import annotations

import common
import quality

SOURCE = common.REPO_ROOT / "src" / "ItemVersion"
LIBS = SOURCE / "Libs"


class TestIsWatched:
    def test_addon_sources_are_watched(self):
        for name in ("Init.lua", "ItemVersion.toc", "Libs.xml"):
            assert quality.is_watched(str(SOURCE / name), LIBS), name

    def test_nested_sources_are_watched(self):
        assert quality.is_watched(str(SOURCE / "Locales" / "deDE.lua"), LIBS)

    def test_other_extensions_are_not(self):
        for name in ("icon.tga", "notes.md", "ItemVersion.lua.bak", "Init"):
            assert not quality.is_watched(str(SOURCE / name), LIBS), name

    def test_vendored_libs_are_not_watched(self):
        # The reason the filter exists: Ace3 is large, never edited, and selene
        # skips it anyway.
        assert not quality.is_watched(str(LIBS / "AceAddon-3.0" / "AceAddon-3.0.lua"), LIBS)

    def test_the_libs_dir_itself_is_not_watched(self):
        assert not quality.is_watched(str(LIBS), LIBS)

    def test_a_lua_file_merely_named_libs_is_watched(self):
        # Libs.xml and a Libs.lua live in the addon root and are ours.
        assert quality.is_watched(str(SOURCE / "Libs.lua"), LIBS)


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
