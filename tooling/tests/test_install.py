"""Tests for linking the addon into a local WoW install.

install writes into a real WoW directory, so the interesting cases are the ones
where it must not: a real addon directory sitting at the target, and a symlink
that must be replaced rather than followed into."""

from __future__ import annotations

import urllib.error
from pathlib import Path
from zipfile import ZipFile

import pytest  # type: ignore[ty:unresolved-import]
from dotenv import dotenv_values  # type: ignore[ty:unresolved-import]

import common
import config
import install
from config import Config

NAME = "ItemVersion"


def make_config(name: str = NAME) -> Config:
    return Config(name=name, curseforge_project_id=1, dev_only=(), libs=(("AceAddon-3.0", "svn://x"),))


def make_wow_root(tmp_path: Path, flavors: tuple[str, ...] = install.FLAVORS) -> Path:
    root = tmp_path / "World of Warcraft"
    for flavor in flavors:
        (root / flavor / "Interface" / "AddOns").mkdir(parents=True)
    return root


@pytest.fixture
def installed(tmp_path, monkeypatch):
    """A fake WoW root and a fake source dir, wired up so install can run."""
    monkeypatch.setattr(config, "SRC_ROOT", tmp_path / "src")
    cfg = make_config()
    (cfg.libs_dir).mkdir(parents=True)
    (cfg.locales_dir).mkdir(parents=True)
    (cfg.locales_dir / "enUS.lua").write_text("-- generated\n", encoding="utf-8")
    (cfg.toc_path).write_text("## Version: 2026.28.0\n", encoding="utf-8")

    root = make_wow_root(tmp_path)

    monkeypatch.setattr(install, "load_config", lambda: cfg)
    # Never let a real .env leak into a test run.
    monkeypatch.setattr(install, "ENV_FILE", tmp_path / "nonexistent")
    monkeypatch.setenv("WOW_ROOT", str(root))

    return root


class TestEnvTemplate:
    def test_configures_nothing_as_shipped(self):
        assert dotenv_values(common.REPO_ROOT / ".env.template").get("WOW_ROOT") is None

    def test_its_examples_survive_uncommenting(self, tmp_path):
        # The Windows example is the reason this exists. dotenv applies escape
        # sequences inside double quotes, so a quoted C:\new\wow comes back with a
        # real newline and tab in it. The template says to leave the value
        # unquoted; this is what makes that advice true rather than folklore.
        template = (common.REPO_ROOT / ".env.template").read_text(encoding="utf-8")
        examples = [
            line.removeprefix("# ")
            for line in template.splitlines()
            if line.startswith("# WOW_ROOT=")
        ]
        assert examples, "the template should show at least one example"

        for example in examples:
            path = tmp_path / ".env"
            path.write_text(example, encoding="utf-8")

            value = dotenv_values(path)["WOW_ROOT"]

            assert value == example.removeprefix("WOW_ROOT="), example
            assert "\n" not in value and "\t" not in value, example


class TestResolveWowRoot:
    def test_uses_the_value(self, tmp_path):
        assert install.resolve_wow_root(str(tmp_path)) == tmp_path

    def test_nothing_configured_dies(self):
        with pytest.raises(common.Die, match="no WoW root configured"):
            install.resolve_wow_root(None)

    def test_empty_dies(self):
        with pytest.raises(common.Die, match="no WoW root configured"):
            install.resolve_wow_root("")

    def test_missing_directory_dies(self, tmp_path):
        with pytest.raises(common.Die, match="not a directory"):
            install.resolve_wow_root(str(tmp_path / "nope"))

    def test_a_file_is_not_a_directory(self, tmp_path):
        target = tmp_path / "file"
        target.write_text("", encoding="utf-8")
        with pytest.raises(common.Die, match="not a directory"):
            install.resolve_wow_root(str(target))


class TestWowRootFromEnvFile:
    def test_reads_dot_env(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text(f"WOW_ROOT={tmp_path}\n", encoding="utf-8")
        monkeypatch.setattr(install, "ENV_FILE", env_file)
        monkeypatch.delenv("WOW_ROOT", raising=False)

        assert install.wow_root() == tmp_path

    def test_a_real_env_var_wins_over_dot_env(self, tmp_path, monkeypatch):
        other = tmp_path / "other"
        other.mkdir()
        env_file = tmp_path / ".env"
        env_file.write_text(f"WOW_ROOT={tmp_path}\n", encoding="utf-8")
        monkeypatch.setattr(install, "ENV_FILE", env_file)
        monkeypatch.setenv("WOW_ROOT", str(other))

        assert install.wow_root() == other

    def test_no_dot_env_and_no_var_dies(self, tmp_path, monkeypatch):
        monkeypatch.setattr(install, "ENV_FILE", tmp_path / "nonexistent")
        monkeypatch.delenv("WOW_ROOT", raising=False)

        with pytest.raises(common.Die, match="no WoW root configured"):
            install.wow_root()


class TestClassify:
    def test_absent(self, tmp_path):
        assert install.classify(tmp_path / "nope") == "absent"

    def test_real_dir(self, tmp_path):
        assert install.classify(tmp_path) == "real-dir"

    def test_link_ok(self, tmp_path):
        target = tmp_path / "link"
        target.symlink_to(tmp_path, target_is_directory=True)
        assert install.classify(target) == "link-ok"

    def test_link_broken(self, tmp_path):
        target = tmp_path / "link"
        target.symlink_to(tmp_path / "gone", target_is_directory=True)
        assert install.classify(target) == "link-broken"


class TestLink:
    def test_creates_the_link(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        dst = tmp_path / "dst"

        install.link(src, dst)

        assert dst.is_symlink()
        assert dst.resolve() == src.resolve()

    def test_replaces_an_existing_link_rather_than_nesting_inside_it(self, tmp_path):
        old = tmp_path / "old"
        old.mkdir()
        new = tmp_path / "new"
        new.mkdir()
        dst = tmp_path / "dst"

        install.link(old, dst)
        install.link(new, dst)

        assert dst.resolve() == new.resolve()
        # The bug this guards: following the old link and creating src/dst inside it.
        assert not (old / "dst").exists()


class TestInstall:
    def test_links_every_flavor(self, installed):
        assert install.cmd_install() == 0

        for flavor in install.FLAVORS:
            assert install.target_for(installed, flavor, NAME).is_symlink()

    def test_refuses_to_clobber_a_real_directory(self, installed, capsys):
        target = install.target_for(installed, "_retail_", NAME)
        target.mkdir()
        (target / "keepme.lua").write_text("-- someone else's install", encoding="utf-8")

        install.cmd_install()

        assert not target.is_symlink()
        assert (target / "keepme.lua").exists()
        assert "REFUSED" in capsys.readouterr().out

    def test_skips_a_flavor_with_no_addons_dir(self, tmp_path, installed, capsys):
        import shutil

        shutil.rmtree(installed / "_classic_")

        install.cmd_install()

        assert "skip, no AddOns dir" in capsys.readouterr().out
        assert not (installed / "_classic_").exists()

    def test_is_idempotent(self, installed):
        install.cmd_install()
        install.cmd_install()

        target = install.target_for(installed, "_retail_", NAME)
        assert target.is_symlink()
        assert target.resolve() == install.load_config().source_dir.resolve()

    def test_unprepared_dies_before_linking(self, installed):
        import shutil

        shutil.rmtree(install.load_config().libs_dir)

        with pytest.raises(common.Die, match="dev prepare-src"):
            install.cmd_install()

        assert not install.target_for(installed, "_retail_", NAME).exists()

    def test_missing_locales_dies_before_linking(self, installed):
        (install.load_config().locales_dir / "enUS.lua").unlink()

        with pytest.raises(common.Die, match="locale files"):
            install.cmd_install()

        assert not install.target_for(installed, "_retail_", NAME).exists()

    def test_flavor_installs_only_the_named_ones(self, installed):
        install.cmd_install(flavors=["retail", "classic"])

        assert install.target_for(installed, "_retail_", NAME).is_symlink()
        assert install.target_for(installed, "_classic_", NAME).is_symlink()
        assert not install.target_for(installed, "_classic_era_", NAME).exists()
        assert not install.target_for(installed, "_anniversary_", NAME).exists()


class TestSelectedFlavors:
    def test_no_selection_means_every_flavor(self):
        assert install.selected_flavors(None) == install.FLAVORS

    def test_all_means_every_flavor(self):
        assert install.selected_flavors(["all"]) == install.FLAVORS

    def test_names_map_to_directories_in_order(self):
        assert install.selected_flavors(["classic", "retail"]) == ("_classic_", "_retail_")

    def test_all_with_a_named_flavor_is_refused(self):
        with pytest.raises(common.Die, match="all"):
            install.selected_flavors(["all", "retail"])


class TestUninstall:
    def test_removes_our_links(self, installed):
        install.cmd_install()
        assert install.cmd_uninstall() == 0

        for flavor in install.FLAVORS:
            assert not install.target_for(installed, flavor, NAME).exists()

    def test_leaves_a_real_directory_alone(self, installed, capsys):
        target = install.target_for(installed, "_retail_", NAME)
        target.mkdir()
        (target / "keepme.lua").write_text("-- someone else's install", encoding="utf-8")

        install.cmd_uninstall()

        assert (target / "keepme.lua").exists()
        assert "left alone" in capsys.readouterr().out

    def test_removes_a_broken_link(self, installed):
        target = install.target_for(installed, "_retail_", NAME)
        target.symlink_to(installed / "gone", target_is_directory=True)

        install.cmd_uninstall()

        assert not target.is_symlink()

    def test_does_not_delete_the_source(self, installed):
        install.cmd_install()
        install.cmd_uninstall()

        assert install.load_config().source_dir.is_dir()
        assert (install.load_config().source_dir / "Libs").is_dir()


class TestStatus:
    def test_reports_each_state(self, installed, capsys):
        install.link(install.load_config().source_dir, install.target_for(installed, "_retail_", NAME))
        install.target_for(installed, "_classic_", NAME).symlink_to(installed / "gone")
        real = install.target_for(installed, "_classic_era_", NAME)
        real.mkdir()
        (real / f"{NAME}.toc").write_text("## Version: 1.2.3\n", encoding="utf-8")

        assert install.cmd_install_status() == 0

        out = capsys.readouterr().out
        assert "symlink ->" in out
        assert "BROKEN symlink ->" in out
        assert "real directory, version 1.2.3" in out
        assert "not installed" in out


class TestResolveSource:
    def test_default_is_local(self):
        assert install.resolve_source().mode == install.LOCAL

    def test_local_flag_is_local(self):
        assert install.resolve_source(local=True).mode == install.LOCAL

    def test_gh_carries_the_tag(self):
        source = install.resolve_source(gh="1.2.3")
        assert source.mode == install.GH
        assert source.ref == "1.2.3"

    def test_cf_carries_the_file_id_as_a_string(self):
        source = install.resolve_source(cf=999)
        assert source.mode == install.CF
        assert source.ref == "999"


class TestMarker:
    def test_roundtrips(self, tmp_path):
        target = tmp_path / NAME
        target.mkdir()
        (target / f"{NAME}.toc").write_text("## Version: 2.0.0\n", encoding="utf-8")

        install.write_marker(make_config(), target, install.Source(install.GH, "2.0.0"))

        assert install.is_our_copy(target)
        marker = install.read_marker(target)
        assert marker["source"] == "gh"
        assert marker["ref"] == "2.0.0"
        assert marker["version"] == "2.0.0"

    def test_an_unmarked_dir_is_not_ours(self, tmp_path):
        target = tmp_path / NAME
        target.mkdir()
        assert not install.is_our_copy(target)
        assert install.read_marker(target) is None

    def test_a_symlink_is_not_a_copy(self, tmp_path):
        target = tmp_path / "link"
        target.symlink_to(tmp_path, target_is_directory=True)
        assert not install.is_our_copy(target)


class TestInstallRemote:
    @pytest.fixture
    def payload(self, tmp_path, monkeypatch):
        """A fake extracted build, wired in so acquire returns it without a download."""
        folder = tmp_path / "payload" / NAME
        folder.mkdir(parents=True)
        (folder / f"{NAME}.toc").write_text("## Version: 9.9.9\n", encoding="utf-8")
        (folder / "Core.lua").write_text("-- published\n", encoding="utf-8")
        monkeypatch.setattr(install, "acquire", lambda config, source, dest: folder)
        return folder

    def test_copies_a_gh_build_into_every_flavor(self, installed, payload):
        assert install.cmd_install(gh="9.9.9") == 0

        for flavor in install.FLAVORS:
            target = install.target_for(installed, flavor, NAME)
            assert not target.is_symlink()
            assert (target / "Core.lua").is_file()
            assert install.is_our_copy(target)

    def test_records_a_marker(self, installed, payload):
        install.cmd_install(gh="9.9.9")

        marker = install.read_marker(install.target_for(installed, "_retail_", NAME))
        assert marker["source"] == "gh"
        assert marker["ref"] == "9.9.9"
        assert marker["version"] == "9.9.9"

    def test_does_not_require_a_prepared_source(self, installed, payload):
        import shutil

        # A downloaded build is self-contained, so a missing local Libs must not
        # stop it the way it stops a symlink install.
        shutil.rmtree(install.load_config().libs_dir)

        assert install.cmd_install(gh="9.9.9") == 0

    def test_refuses_a_foreign_directory_without_force(self, installed, payload, capsys):
        target = install.target_for(installed, "_retail_", NAME)
        target.mkdir()
        (target / "keepme.lua").write_text("-- someone else's install", encoding="utf-8")

        install.cmd_install(gh="9.9.9")

        assert (target / "keepme.lua").exists()
        assert "REFUSED" in capsys.readouterr().out

    def test_force_replaces_a_foreign_directory(self, installed, payload):
        target = install.target_for(installed, "_retail_", NAME)
        target.mkdir()
        (target / "keepme.lua").write_text("-- someone else's install", encoding="utf-8")

        install.cmd_install(gh="9.9.9", force=True)

        assert not (target / "keepme.lua").exists()
        assert (target / "Core.lua").is_file()

    def test_replaces_our_own_copy_without_force(self, installed, payload):
        install.cmd_install(gh="9.9.9")
        assert install.cmd_install(gh="9.9.9") == 0

        target = install.target_for(installed, "_retail_", NAME)
        assert install.is_our_copy(target)
        assert (target / "Core.lua").is_file()

    def test_replaces_a_local_symlink(self, installed, payload):
        install.cmd_install()
        assert install.cmd_install(gh="9.9.9") == 0

        target = install.target_for(installed, "_retail_", NAME)
        assert not target.is_symlink()
        assert install.is_our_copy(target)


class TestUninstallDevCopy:
    def test_removes_a_marked_copy(self, installed):
        target = install.target_for(installed, "_retail_", NAME)
        target.mkdir()
        (target / f"{NAME}.toc").write_text("## Version: 9.9.9\n", encoding="utf-8")
        install.write_marker(install.load_config(), target, install.Source(install.GH, "9.9.9"))

        install.cmd_uninstall()

        assert not target.exists()

    def test_leaves_an_unmarked_directory_alone(self, installed, capsys):
        target = install.target_for(installed, "_retail_", NAME)
        target.mkdir()
        (target / "keepme.lua").write_text("-- someone else's install", encoding="utf-8")

        install.cmd_uninstall()

        assert (target / "keepme.lua").exists()
        assert "left alone" in capsys.readouterr().out


class TestStatusDevCopy:
    def test_reports_a_dev_copy(self, installed, capsys):
        target = install.target_for(installed, "_retail_", NAME)
        target.mkdir()
        (target / f"{NAME}.toc").write_text("## Version: 9.9.9\n", encoding="utf-8")
        install.write_marker(install.load_config(), target, install.Source(install.CF, "12345"))

        install.cmd_install_status()

        assert "dev copy from cf 12345, version 9.9.9" in capsys.readouterr().out


class TestDownloadGh:
    def test_downloads_and_returns_the_zip(self, tmp_path, monkeypatch):
        monkeypatch.setattr(install, "require_tool", lambda name: name)

        def fake_run(command):
            dest = Path(command[command.index("--dir") + 1])
            (dest / f"{NAME}-1.2.3.zip").write_bytes(b"zip")
            return 0

        monkeypatch.setattr(install, "run", fake_run)

        result = install.download_gh(make_config(), "1.2.3", tmp_path)
        assert result == tmp_path / f"{NAME}-1.2.3.zip"

    def test_a_tag_is_passed_positionally(self, tmp_path, monkeypatch):
        seen = {}
        monkeypatch.setattr(install, "require_tool", lambda name: name)

        def fake_run(command):
            seen["command"] = command
            dest = Path(command[command.index("--dir") + 1])
            (dest / f"{NAME}-1.2.3.zip").write_bytes(b"zip")
            return 0

        monkeypatch.setattr(install, "run", fake_run)

        install.download_gh(make_config(), "1.2.3", tmp_path)
        assert seen["command"][3] == "1.2.3"

    def test_latest_omits_the_tag(self, tmp_path, monkeypatch):
        seen = {}
        monkeypatch.setattr(install, "require_tool", lambda name: name)

        def fake_run(command):
            seen["command"] = command
            dest = Path(command[command.index("--dir") + 1])
            (dest / f"{NAME}-9.9.9.zip").write_bytes(b"zip")
            return 0

        monkeypatch.setattr(install, "run", fake_run)

        install.download_gh(make_config(), "latest", tmp_path)
        # No positional tag, so the first thing after download is a flag.
        assert seen["command"][3].startswith("--")

    def test_a_failed_download_dies(self, tmp_path, monkeypatch):
        monkeypatch.setattr(install, "require_tool", lambda name: name)
        monkeypatch.setattr(install, "run", lambda command: 1)

        with pytest.raises(common.Die, match="gh release download failed"):
            install.download_gh(make_config(), "1.2.3", tmp_path)

    def test_no_matching_zip_dies(self, tmp_path, monkeypatch):
        monkeypatch.setattr(install, "require_tool", lambda name: name)
        monkeypatch.setattr(install, "run", lambda command: 0)

        with pytest.raises(common.Die, match="no ItemVersion"):
            install.download_gh(make_config(), "1.2.3", tmp_path)


class FakeResponse:
    def __init__(self, body: bytes):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self) -> bytes:
        return self.body


class TestDownloadCf:
    def test_downloads_by_id(self, tmp_path, monkeypatch):
        seen = {}

        def fake_urlopen(request, timeout=0):
            seen["url"] = request.full_url
            return FakeResponse(b"ZIPBYTES")

        monkeypatch.setattr(install.urllib.request, "urlopen", fake_urlopen)

        result = install.download_cf(make_config(), "12345", tmp_path)

        assert result.read_bytes() == b"ZIPBYTES"
        assert "mods/1/files/12345/download" in seen["url"]

    def test_an_http_error_dies(self, tmp_path, monkeypatch):
        def fake_urlopen(request, timeout=0):
            raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)

        monkeypatch.setattr(install.urllib.request, "urlopen", fake_urlopen)

        with pytest.raises(common.Die, match="CurseForge download failed .404."):
            install.download_cf(make_config(), "12345", tmp_path)


class TestExtractAddon:
    def test_extracts_the_addon_folder(self, tmp_path):
        source = tmp_path / "build" / NAME
        source.mkdir(parents=True)
        (source / f"{NAME}.toc").write_text("## Version: 1.0.0\n", encoding="utf-8")

        archive = tmp_path / "build.zip"
        with ZipFile(archive, "w") as zip_file:
            zip_file.write(source / f"{NAME}.toc", f"{NAME}/{NAME}.toc")

        folder = install.extract_addon(make_config(), archive, tmp_path / "out")
        assert (folder / f"{NAME}.toc").is_file()

    def test_a_zip_without_the_addon_folder_dies(self, tmp_path):
        archive = tmp_path / "build.zip"
        with ZipFile(archive, "w") as zip_file:
            zip_file.writestr("readme.txt", "hi")

        with pytest.raises(common.Die, match="no ItemVersion/ folder"):
            install.extract_addon(make_config(), archive, tmp_path / "out")
