"""Tests for fetching libraries and building the addon zip."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from zipfile import ZipFile

import pytest  # type: ignore[ty:unresolved-import]

import common
import config
import packaging
from config import Config


@pytest.fixture
def packager(tmp_path, monkeypatch):
    """A fake addon source and a redirected dist, with svn stubbed out.

    Named packager, not packaging: a fixture called packaging would shadow the
    module it patches.
    """
    monkeypatch.setattr(config, "SRC_ROOT", tmp_path / "src")
    cfg = Config(
        name="ItemVersion",
        curseforge_project_id=1,
        ignore=("Bindings.xml",),
        libs=(("AceAddon-3.0", "svn://example/AceAddon-3.0"),),
    )

    source = cfg.source_dir
    (source / "Libs" / "AceAddon-3.0").mkdir(parents=True)
    (source / "Libs" / "AceAddon-3.0" / "AceAddon-3.0.lua").write_text("-- lib", encoding="utf-8")
    (cfg.toc_path).write_text(
        "## Title: ItemVersion\n## Version: 1.2.3\n\nLocales\\enUS.lua\nInit.lua\n",
        encoding="utf-8",
    )
    (source / "Init.lua").write_text("-- code\n", encoding="utf-8")
    (source / "Bindings.xml").write_text("<Bindings/>\n", encoding="utf-8")

    calls: list[list[str]] = []

    def fake_run(command):
        calls.append(command)
        if command[:2] == ["svn", "export"]:
            Path(command[-1]).mkdir(parents=True, exist_ok=True)
        return 0

    monkeypatch.setattr(packaging, "BUILD_ROOT", tmp_path / "dist")
    monkeypatch.setattr(packaging, "load_config", lambda: cfg)
    monkeypatch.setattr(packaging, "run", fake_run)
    monkeypatch.setattr(packaging, "require_tool", lambda name: name)
    monkeypatch.setattr(common, "REPO_ROOT", tmp_path)

    return SimpleNamespace(source=source, build_root=tmp_path / "dist", config=cfg, calls=calls)


class TestStampBuildDate:
    def test_adds_the_field_after_the_header(self):
        toc = "## Title: X\n## Version: 1.0\n\nInit.lua\n"
        when = datetime(2026, 7, 17, 21, 37, 11, tzinfo=timezone.utc)

        result = packaging.stamp_build_date(toc, when)

        lines = result.splitlines()
        assert lines[2] == "## X-Build-Date-Time: 2026-07-17T21:37:11Z"
        # still before the file list
        assert "Init.lua" in lines[4]

    def test_preserves_crlf(self):
        toc = "## Version: 1.0\r\n\r\nInit.lua\r\n"
        result = packaging.stamp_build_date(toc, datetime(2026, 1, 1, tzinfo=timezone.utc))
        assert "## X-Build-Date-Time: 2026-01-01T00:00:00Z\r\n" in result


class TestBuild:
    def test_produces_a_zip_rooted_at_the_addon(self, packager):
        assert packaging.cmd_build() == 0

        archive = packager.build_root / "ItemVersion-1.2.3.zip"
        assert archive.exists()

        names = ZipFile(archive).namelist()
        assert "ItemVersion/Init.lua" in names
        assert "ItemVersion/Libs/AceAddon-3.0/AceAddon-3.0.lua" in names

    def test_leaves_out_ignored_files(self, packager):
        packaging.cmd_build()

        staged = packager.build_root / "ItemVersion"
        assert not (staged / "Bindings.xml").exists()
        assert "ItemVersion/Bindings.xml" not in ZipFile(
            packager.build_root / "ItemVersion-1.2.3.zip"
        ).namelist()

    def test_stamps_the_build_date_into_the_staged_toc(self, packager):
        packaging.cmd_build()

        toc = (packager.build_root / "ItemVersion" / "ItemVersion.toc").read_text(encoding="utf-8")
        assert "## X-Build-Date-Time:" in toc

    def test_does_not_touch_the_source_toc(self, packager):
        packaging.cmd_build()

        assert "X-Build-Date-Time" not in packager.source.joinpath(
            "ItemVersion.toc"
        ).read_text(encoding="utf-8")

    def test_rebuild_replaces_the_previous_stage(self, packager):
        packaging.cmd_build()
        stale = packager.build_root / "ItemVersion" / "stale.lua"
        stale.write_text("-- left over", encoding="utf-8")

        packaging.cmd_build()

        assert not stale.exists()

    def test_fetches_missing_libs_first(self, packager, monkeypatch):
        import shutil

        shutil.rmtree(packager.source / "Libs" / "AceAddon-3.0")

        packaging.cmd_build()

        assert ["svn", "export", "--quiet", "svn://example/AceAddon-3.0",
                str(packager.source / "Libs" / "AceAddon-3.0")] in packager.calls


class TestPrepare:
    def test_present_libs_are_not_refetched(self, packager, capsys):
        assert packaging.cmd_prepare_src() == 0

        assert packager.calls == []
        assert "present" in capsys.readouterr().out

    def test_missing_libs_are_exported(self, packager):
        import shutil

        shutil.rmtree(packager.source / "Libs" / "AceAddon-3.0")

        assert packaging.cmd_prepare_src() == 0
        assert any(command[:2] == ["svn", "export"] for command in packager.calls)

    def test_a_failed_export_dies(self, packager, monkeypatch):
        import shutil

        shutil.rmtree(packager.source / "Libs" / "AceAddon-3.0")
        monkeypatch.setattr(packaging, "run", lambda command: 1)

        with pytest.raises(common.Die, match="could not export"):
            packaging.cmd_prepare_src()

    def test_generates_locale_files_and_syncs_the_toc(self, packager):
        packager.config.translations_path.write_text(
            "- key: Hello\n  translations:\n    deDE: Hallo\n", encoding="utf-8"
        )

        assert packaging.cmd_prepare_src() == 0

        locales_dir = packager.source / "Locales"
        assert (locales_dir / "enUS.lua").is_file()
        assert (locales_dir / "deDE.lua").is_file()
        toc = packager.config.toc_path.read_text(encoding="utf-8")
        assert "Locales\\deDE.lua" in toc

    def test_drops_a_locale_that_lost_its_translations(self, packager):
        packager.config.translations_path.write_text(
            "- key: Hello\n  translations: {}\n", encoding="utf-8"
        )
        stale = packager.source / "Locales" / "deDE.lua"
        stale.parent.mkdir(parents=True, exist_ok=True)
        stale.write_text("-- left over", encoding="utf-8")

        packaging.cmd_prepare_src()

        assert not stale.exists()


class TestClean:
    def test_removes_the_generated_trees(self, packager, capsys):
        (packager.build_root / "junk").mkdir(parents=True)
        (packager.source / "Locales").mkdir(parents=True)

        assert packaging.cmd_clean() == 0

        assert not packager.build_root.exists()
        assert not (packager.source / "Libs").exists()
        assert not (packager.source / "Locales").exists()
        assert "removed" in capsys.readouterr().out

    def test_is_fine_when_there_is_nothing_to_remove(self, packager):
        import shutil

        shutil.rmtree(packager.source / "Libs")
        assert packaging.cmd_clean() == 0
