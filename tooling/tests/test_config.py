"""Tests for reading wowaddon.yml."""

from __future__ import annotations

import pytest  # type: ignore[ty:unresolved-import]

import common
import config

VALID = """
name: ItemVersion
curseforge-project-id: 433258
ignore:
  - Bindings.xml
libs:
  AceAddon-3.0: svn://example/AceAddon-3.0
  LibStub: svn://example/LibStub
"""


class TestParseConfig:
    def test_reads_every_field(self):
        result = config.parse_config(VALID)

        assert result.name == "ItemVersion"
        assert result.curseforge_project_id == 433258
        assert result.ignore == ("Bindings.xml",)
        assert result.libs == (
            ("AceAddon-3.0", "svn://example/AceAddon-3.0"),
            ("LibStub", "svn://example/LibStub"),
        )

    def test_libs_keep_file_order(self):
        # Order matters only for reproducibility, but assert it so a dict swap
        # that reorders would be caught.
        assert [name for name, _ in config.parse_config(VALID).libs] == [
            "AceAddon-3.0",
            "LibStub",
        ]

    def test_ignore_is_optional(self):
        text = "name: X\ncurseforge-project-id: 1\nlibs:\n  A: svn://x\n"
        assert config.parse_config(text).ignore == ()

    def test_missing_required_key_dies(self):
        text = "name: X\nlibs:\n  A: svn://x\n"
        with pytest.raises(common.Die, match="curseforge-project-id"):
            config.parse_config(text)

    def test_non_integer_project_id_dies(self):
        text = "name: X\ncurseforge-project-id: nope\nlibs:\n  A: svn://x\n"
        with pytest.raises(common.Die, match="integer"):
            config.parse_config(text)

    def test_empty_libs_dies(self):
        text = "name: X\ncurseforge-project-id: 1\nlibs: {}\n"
        with pytest.raises(common.Die, match="libs"):
            config.parse_config(text)

    def test_non_mapping_dies(self):
        with pytest.raises(common.Die, match="object"):
            config.parse_config("- just\n- a\n- list\n")

    def test_unknown_key_dies(self):
        # additionalProperties: false in the schema is what forbids a stray key.
        text = VALID + "surprise: yes\n"
        with pytest.raises(common.Die, match="surprise"):
            config.parse_config(text)


class TestDerivedPaths:
    def test_layout_follows_the_name(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "SRC_ROOT", tmp_path / "src")
        cfg = config.parse_config(VALID)  # name ItemVersion

        assert cfg.source_dir == tmp_path / "src" / "ItemVersion"
        assert cfg.libs_dir == tmp_path / "src" / "ItemVersion" / "Libs"
        assert cfg.toc_path == tmp_path / "src" / "ItemVersion" / "ItemVersion.toc"
        assert cfg.locales_dir == tmp_path / "src" / "ItemVersion" / "Locales"

    def test_translations_live_beside_the_addon_not_inside_it(self, tmp_path, monkeypatch):
        # Outside src/<name>, so it is never symlinked into WoW nor built into the zip.
        monkeypatch.setattr(config, "SRC_ROOT", tmp_path / "src")
        cfg = config.parse_config(VALID)

        assert cfg.translations_path == tmp_path / "src" / "translations.yml"
        assert cfg.source_dir not in cfg.translations_path.parents

    def test_a_rename_moves_the_whole_layout(self, tmp_path, monkeypatch):
        monkeypatch.setattr(config, "SRC_ROOT", tmp_path / "src")
        cfg = config.parse_config(VALID.replace("name: ItemVersion", "name: Renamed"))

        assert cfg.source_dir == tmp_path / "src" / "Renamed"
        assert cfg.toc_path.name == "Renamed.toc"


def test_the_real_config_parses():
    # The committed wowaddon.yml must actually load.
    assert config.load_config().name == "ItemVersion"
