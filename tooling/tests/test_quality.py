"""Tests for the lint/format/watch commands."""

from __future__ import annotations



import quality


class TestIsWatched:
    def test_addon_sources_are_watched(self):
        for name in ("Init.lua", "ItemVersion.toc", "Libs.xml"):
            assert quality.is_watched(str(quality.LINK_SRC / name)), name

    def test_nested_sources_are_watched(self):
        assert quality.is_watched(str(quality.LINK_SRC / "Locales" / "deDE.lua"))

    def test_other_extensions_are_not(self):
        for name in ("icon.tga", "notes.md", "ItemVersion.lua.bak", "Init"):
            assert not quality.is_watched(str(quality.LINK_SRC / name)), name

    def test_vendored_libs_are_not_watched(self):
        # The reason the filter exists: Ace3 is large, never edited, and selene
        # skips it anyway.
        assert not quality.is_watched(str(quality.LIBS_DIR / "AceAddon-3.0" / "AceAddon-3.0.lua"))

    def test_the_libs_dir_itself_is_not_watched(self):
        assert not quality.is_watched(str(quality.LIBS_DIR))

    def test_a_lua_file_merely_named_libs_is_watched(self):
        # Libs.xml and a Libs.lua live in the addon root and are ours.
        assert quality.is_watched(str(quality.LINK_SRC / "Libs.lua"))


class TestDescribe:
    def test_names_the_change_and_a_relative_path(self):
        changes = {(quality.Change.modified, str(quality.LINK_SRC / "Init.lua"))}
        assert quality.describe(changes) == ["modified ItemVersion/Init.lua"]

    def test_is_sorted_and_lists_every_change(self):
        # A list, not a set: set iteration order is arbitrary, so a set can land
        # already sorted and let a missing sort() pass unnoticed. This order is
        # reverse-sorted, so it can only pass if the sort really happens.
        changes = [
            (quality.Change.modified, str(quality.LINK_SRC / "Zed.lua")),
            (quality.Change.deleted, str(quality.LINK_SRC / "Mid.lua")),
            (quality.Change.added, str(quality.LINK_SRC / "Init.lua")),
        ]
        assert quality.describe(changes) == [
            "added ItemVersion/Init.lua",
            "deleted ItemVersion/Mid.lua",
            "modified ItemVersion/Zed.lua",
        ]
