"""Tests for publishing a built addon to CurseForge and GitHub."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest  # type: ignore[ty:unresolved-import]

import common
import config
import publish
from config import Config

WHEN = datetime(2026, 7, 17, 21, 37, 26, tzinfo=timezone.utc)

CONFIG = Config(
    name="ItemVersion",
    curseforge_project_id=433258,
    dev_only=(),
    libs=(("A", "svn://x"),),
    changelog_url="https://example/CHANGELOG.md",
    curseforge_project_slug="itemversion",
)


class TestPureHelpers:
    def test_default_targets_release_goes_everywhere(self):
        assert publish.default_targets("release") == ("curseforge", "github")

    def test_default_targets_prerelease_is_curseforge_only(self):
        assert publish.default_targets("alpha") == ("curseforge",)
        assert publish.default_targets("beta") == ("curseforge",)

    def test_interface_list_splits_the_toc_field(self):
        toc = "## Interface: 120007, 50504, 11508\n"
        assert publish.interface_list(toc) == ("120007", "50504", "11508")

    def test_release_notes_link_to_the_changelog(self):
        notes = publish.release_notes("https://example/CHANGELOG.md")
        assert "https://example/CHANGELOG.md" in notes
        assert "changelog" in notes.lower()

    def test_release_notes_falls_back_without_a_url(self):
        assert publish.release_notes(None) == publish.DEFAULT_NOTES
        assert publish.release_notes("") == publish.DEFAULT_NOTES

    def test_file_id_from_reads_the_id(self):
        assert publish.file_id_from({"id": 20402}) == 20402

    def test_file_id_from_tolerates_a_shapeless_response(self):
        for payload in ({}, {"id": "nope"}, [1, 2], "text", None):
            assert publish.file_id_from(payload) is None

    def test_authors_file_url_points_at_the_dashboard(self):
        assert (
            publish.authors_file_url(433258, 20402)
            == "https://authors.curseforge.com/#/projects/433258/files/20402"
        )

    def test_public_file_url_points_at_the_download_page(self):
        assert (
            publish.public_file_url("itemversion", 20402)
            == "https://www.curseforge.com/wow/addons/itemversion/files/20402"
        )


class TestBuildPlan:
    def test_release_labels_with_the_bare_version(self):
        plan = publish.build_plan(CONFIG, "2026.28.0", ("120007",), "release", "notes", WHEN)
        assert plan.display_name == "2026.28.0"
        assert plan.tag == "2026.28.0"
        assert plan.archive.name == "ItemVersion-2026.28.0.zip"

    def test_alpha_labels_with_a_timestamp(self):
        plan = publish.build_plan(CONFIG, "2026.28.0", ("120007",), "alpha", "notes", WHEN)
        assert plan.display_name == "2026.28.0-alpha.20260717213726"
        # the file on disk is still the plain build; the label carries the distinction
        assert plan.archive.name == "ItemVersion-2026.28.0.zip"

    def test_version_names_come_from_the_interfaces(self):
        plan = publish.build_plan(CONFIG, "1.0", ("120007", "11508"), "release", "n", WHEN)
        assert plan.version_names == ("12.0.7", "1.15.8")


class TestResolveVersionIds:
    CATALOG = [
        {"id": 1, "name": "12.0.7"},
        {"id": 2, "name": "1.15.8"},
        {"id": 3, "name": "5.5.4"},
    ]

    def test_maps_names_to_ids(self):
        assert publish.resolve_version_ids(self.CATALOG, ("12.0.7", "5.5.4")) == [1, 3]

    def test_unknown_version_dies(self):
        with pytest.raises(common.Die, match="9.9.9"):
            publish.resolve_version_ids(self.CATALOG, ("9.9.9",))

    def test_non_list_catalog_dies(self):
        with pytest.raises(common.Die, match="not a list"):
            publish.resolve_version_ids({"nope": True}, ("12.0.7",))


class TestMultipart:
    def test_encodes_metadata_and_file(self):
        boundary, body = publish._multipart({"metadata": "{}"}, "a.zip", b"PK\x03\x04")
        assert boundary.encode() in body
        assert b'name="metadata"' in body
        assert b'filename="a.zip"' in body
        assert b"PK\x03\x04" in body
        assert body.endswith(f"\r\n--{boundary}--\r\n".encode())


@pytest.fixture
def published(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SRC_ROOT", tmp_path / "src")
    CONFIG.toc_path.parent.mkdir(parents=True)
    CONFIG.toc_path.write_text(
        "## Version: 1.2.3\n## Interface: 120007, 11508\n\nInit.lua\n", encoding="utf-8"
    )

    build_root = tmp_path / "dist"
    build_root.mkdir()
    (build_root / "ItemVersion-1.2.3.zip").write_bytes(b"zipdata")

    monkeypatch.setattr(publish, "load_config", lambda: CONFIG)
    monkeypatch.setattr(publish, "BUILD_ROOT", build_root)
    monkeypatch.setattr(common, "REPO_ROOT", tmp_path)

    return SimpleNamespace(build_root=build_root)


class TestPublish:
    def test_dry_run_prints_the_plan_and_uploads_nothing(self, published, monkeypatch, capsys):
        def forbidden(*args):
            raise AssertionError("dry run must not upload")

        monkeypatch.setattr(publish, "upload_curseforge", forbidden)
        monkeypatch.setattr(publish, "upload_github", forbidden)

        assert publish.cmd_publish(dry_run=True) == 0

        out = capsys.readouterr().out
        assert "Release type: release" in out
        assert "12.0.7" in out and "1.15.8" in out
        assert "https://example/CHANGELOG.md" in out

    def test_missing_archive_dies(self, published):
        (published.build_root / "ItemVersion-1.2.3.zip").unlink()

        with pytest.raises(common.Die, match="build"):
            publish.cmd_publish(dry_run=True)

    def test_abort_when_not_confirmed(self, published, monkeypatch):
        uploaded = []
        monkeypatch.setattr(publish, "_confirm", lambda: False)
        monkeypatch.setattr(publish, "upload_curseforge", lambda *a: uploaded.append("cf"))
        monkeypatch.setattr(publish, "upload_github", lambda *a: uploaded.append("gh"))

        assert publish.cmd_publish() == 1
        assert uploaded == []

    def test_release_uploads_to_both_targets(self, published, monkeypatch):
        uploaded = []
        monkeypatch.setattr(publish, "upload_curseforge", lambda *a: uploaded.append("cf"))
        monkeypatch.setattr(publish, "upload_github", lambda *a: uploaded.append("gh"))

        assert publish.cmd_publish(yes=True) == 0
        assert uploaded == ["cf", "gh"]

    def test_alpha_uploads_to_curseforge_only(self, published, monkeypatch):
        uploaded = []
        monkeypatch.setattr(publish, "upload_curseforge", lambda *a: uploaded.append("cf"))
        monkeypatch.setattr(publish, "upload_github", lambda *a: uploaded.append("gh"))

        assert publish.cmd_publish(type="alpha", yes=True) == 0
        assert uploaded == ["cf"]


class TestCfToken:
    def test_missing_token_dies(self, monkeypatch, tmp_path):
        monkeypatch.setattr(publish, "ENV_FILE", tmp_path / "nonexistent")
        monkeypatch.delenv(publish.CF_TOKEN_ENV, raising=False)

        with pytest.raises(common.Die, match="token"):
            publish.cf_token()
