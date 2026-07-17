"""Tests for fetching externals and building a release."""

from __future__ import annotations


import pytest  # type: ignore[ty:unresolved-import]

import common
import packaging


@pytest.fixture
def packager(tmp_path, monkeypatch):
    """Redirect the packaging paths into tmp and stub out release.sh.

    Named packager, not packaging: a fixture called packaging would shadow the
    module it patches.
    """
    calls = []

    def fake_run(command):
        calls.append(command)
        # Stand in for what release.sh -z leaves behind.
        (tmp_path / ".release" / common.SOURCE_DIR / "Libs" / "AceAddon-3.0").mkdir(parents=True)
        return 0

    monkeypatch.setattr(packaging, "BUILD_ROOT", tmp_path / ".release")
    monkeypatch.setattr(packaging, "BUILD_LIBS_DIR", tmp_path / ".release" / common.SOURCE_DIR / "Libs")
    monkeypatch.setattr(packaging, "LIBS_DIR", tmp_path / "src" / common.SOURCE_DIR / "Libs")
    monkeypatch.setattr(common, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(packaging, "require_tool", lambda name: name)
    monkeypatch.setattr(packaging, "run", fake_run)

    return calls


class TestLibs:
    def test_fetches_and_copies_into_place(self, packager):
        assert packaging.cmd_libs() == 0

        assert packager == [["release.sh", "-z"]]
        assert (packaging.LIBS_DIR / "AceAddon-3.0").is_dir()

    def test_is_a_no_op_when_libs_are_present(self, packager, capsys):
        packaging.LIBS_DIR.mkdir(parents=True)

        assert packaging.cmd_libs() == 0

        assert packager == [], "should not have shelled out to release.sh"
        assert "already present" in capsys.readouterr().out

    def test_a_failed_fetch_does_not_copy(self, packager, monkeypatch):
        monkeypatch.setattr(packaging, "run", lambda command: 1)

        assert packaging.cmd_libs() == 1
        assert not packaging.LIBS_DIR.exists()


class TestClean:
    def test_removes_both_trees(self, packager, capsys):
        (packaging.BUILD_ROOT / "junk").mkdir(parents=True)
        (packaging.LIBS_DIR / "AceAddon-3.0").mkdir(parents=True)

        assert packaging.cmd_clean() == 0

        assert not packaging.BUILD_ROOT.exists()
        assert not packaging.LIBS_DIR.exists()
        assert "removed" in capsys.readouterr().out

    def test_is_fine_when_there_is_nothing_to_remove(self, packager):
        assert packaging.cmd_clean() == 0

    def test_leaves_the_source_alone(self, packager):
        (packaging.LIBS_DIR / "AceAddon-3.0").mkdir(parents=True)
        source = packaging.LIBS_DIR.parent
        (source / "Init.lua").write_text("-- keep me", encoding="utf-8")

        packaging.cmd_clean()

        assert (source / "Init.lua").exists()


class TestBuild:
    def test_shells_out_to_the_packager(self, packager):
        assert packaging.cmd_build() == 0
        assert packager == [["release.sh", "-ze"]]
