# /// script
# requires-python = ">=3.11"
# dependencies = ["pytest>=8", "python-dotenv>=1.0", "watchfiles>=1.0"]
# ///
"""Tests for the dev helpers.

  uv run scripts/test_dev.py

install writes into a real WoW directory, so the interesting cases are the ones
where it must not: a real addon directory sitting at the target, and a symlink
that must be replaced rather than followed into.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest  # type: ignore[ty:unresolved-import]
from dotenv import dotenv_values  # type: ignore[ty:unresolved-import]

sys.path.insert(0, str(Path(__file__).parent))

import dev  # noqa: E402


def make_wow_root(tmp_path: Path, flavors: tuple[str, ...] = dev.FLAVORS) -> Path:
    root = tmp_path / "World of Warcraft"
    for flavor in flavors:
        (root / flavor / "Interface" / "AddOns").mkdir(parents=True)
    return root


@pytest.fixture
def installed(tmp_path, monkeypatch):
    """A fake WoW root and a fake source dir, wired up so install can run."""
    source = tmp_path / "src" / dev.SOURCE_DIR
    (source / "Libs").mkdir(parents=True)
    (source / f"{dev.SOURCE_DIR}.toc").write_text("## Version: 2026.28.0\n", encoding="utf-8")

    root = make_wow_root(tmp_path)

    monkeypatch.setattr(dev, "LINK_SRC", source)
    monkeypatch.setattr(dev, "LIBS_DIR", source / "Libs")
    # Never let a real .env leak into a test run.
    monkeypatch.setattr(dev, "ENV_FILE", tmp_path / "nonexistent")
    monkeypatch.setenv("WOW_ROOT", str(root))

    return root


class TestEnvTemplate:
    def test_configures_nothing_as_shipped(self):
        assert dotenv_values(dev.REPO_ROOT / ".env.template").get("WOW_ROOT") is None

    def test_its_examples_survive_uncommenting(self, tmp_path):
        # The Windows example is the reason this exists. dotenv applies escape
        # sequences inside double quotes, so a quoted C:\new\wow comes back with a
        # real newline and tab in it. The template says to leave the value
        # unquoted; this is what makes that advice true rather than folklore.
        template = (dev.REPO_ROOT / ".env.template").read_text(encoding="utf-8")
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
        assert dev.resolve_wow_root(str(tmp_path)) == tmp_path

    def test_nothing_configured_dies(self):
        with pytest.raises(dev.Die, match="no WoW root configured"):
            dev.resolve_wow_root(None)

    def test_empty_dies(self):
        with pytest.raises(dev.Die, match="no WoW root configured"):
            dev.resolve_wow_root("")

    def test_missing_directory_dies(self, tmp_path):
        with pytest.raises(dev.Die, match="not a directory"):
            dev.resolve_wow_root(str(tmp_path / "nope"))

    def test_a_file_is_not_a_directory(self, tmp_path):
        target = tmp_path / "file"
        target.write_text("", encoding="utf-8")
        with pytest.raises(dev.Die, match="not a directory"):
            dev.resolve_wow_root(str(target))


class TestWowRootFromEnvFile:
    def test_reads_dot_env(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text(f"WOW_ROOT={tmp_path}\n", encoding="utf-8")
        monkeypatch.setattr(dev, "ENV_FILE", env_file)
        monkeypatch.delenv("WOW_ROOT", raising=False)

        assert dev.wow_root() == tmp_path

    def test_a_real_env_var_wins_over_dot_env(self, tmp_path, monkeypatch):
        other = tmp_path / "other"
        other.mkdir()
        env_file = tmp_path / ".env"
        env_file.write_text(f"WOW_ROOT={tmp_path}\n", encoding="utf-8")
        monkeypatch.setattr(dev, "ENV_FILE", env_file)
        monkeypatch.setenv("WOW_ROOT", str(other))

        assert dev.wow_root() == other

    def test_no_dot_env_and_no_var_dies(self, tmp_path, monkeypatch):
        monkeypatch.setattr(dev, "ENV_FILE", tmp_path / "nonexistent")
        monkeypatch.delenv("WOW_ROOT", raising=False)

        with pytest.raises(dev.Die, match="no WoW root configured"):
            dev.wow_root()


class TestVersionFromToc:
    def test_reads_the_version(self):
        assert dev.version_from_toc("## Title: X\n## Version: 2026.28.0\n") == "2026.28.0"

    def test_missing_version_is_none(self):
        assert dev.version_from_toc("## Title: X\n") is None

    def test_ignores_a_version_further_in(self):
        assert dev.version_from_toc("## X-Foo: ## Version: nope\n") is None


class TestClassify:
    def test_absent(self, tmp_path):
        assert dev.classify(tmp_path / "nope") == "absent"

    def test_real_dir(self, tmp_path):
        assert dev.classify(tmp_path) == "real-dir"

    def test_link_ok(self, tmp_path):
        target = tmp_path / "link"
        target.symlink_to(tmp_path, target_is_directory=True)
        assert dev.classify(target) == "link-ok"

    def test_link_broken(self, tmp_path):
        target = tmp_path / "link"
        target.symlink_to(tmp_path / "gone", target_is_directory=True)
        assert dev.classify(target) == "link-broken"


class TestLink:
    def test_creates_the_link(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        dst = tmp_path / "dst"

        dev.link(src, dst)

        assert dst.is_symlink()
        assert dst.resolve() == src.resolve()

    def test_replaces_an_existing_link_rather_than_nesting_inside_it(self, tmp_path):
        old = tmp_path / "old"
        old.mkdir()
        new = tmp_path / "new"
        new.mkdir()
        dst = tmp_path / "dst"

        dev.link(old, dst)
        dev.link(new, dst)

        assert dst.resolve() == new.resolve()
        # The bug this guards: following the old link and creating src/dst inside it.
        assert not (old / "dst").exists()


class TestInstall:
    def test_links_every_flavor(self, installed):
        assert dev.cmd_install() == 0

        for flavor in dev.FLAVORS:
            assert dev.target_for(installed, flavor).is_symlink()

    def test_refuses_to_clobber_a_real_directory(self, installed, capsys):
        target = dev.target_for(installed, "_retail_")
        target.mkdir()
        (target / "keepme.lua").write_text("-- someone else's install", encoding="utf-8")

        dev.cmd_install()

        assert not target.is_symlink()
        assert (target / "keepme.lua").exists()
        assert "REFUSED" in capsys.readouterr().out

    def test_skips_a_flavor_with_no_addons_dir(self, tmp_path, installed, capsys):
        import shutil

        shutil.rmtree(installed / "_classic_")

        dev.cmd_install()

        assert "skip, no AddOns dir" in capsys.readouterr().out
        assert not (installed / "_classic_").exists()

    def test_is_idempotent(self, installed):
        dev.cmd_install()
        dev.cmd_install()

        target = dev.target_for(installed, "_retail_")
        assert target.is_symlink()
        assert target.resolve() == dev.LINK_SRC.resolve()

    def test_missing_libs_dies_before_linking(self, installed, monkeypatch):
        monkeypatch.setattr(dev, "LIBS_DIR", installed / "nope")

        with pytest.raises(dev.Die, match="dev.py libs"):
            dev.cmd_install()

        assert not dev.target_for(installed, "_retail_").exists()


class TestUninstall:
    def test_removes_our_links(self, installed):
        dev.cmd_install()
        assert dev.cmd_uninstall() == 0

        for flavor in dev.FLAVORS:
            assert not dev.target_for(installed, flavor).exists()

    def test_leaves_a_real_directory_alone(self, installed, capsys):
        target = dev.target_for(installed, "_retail_")
        target.mkdir()
        (target / "keepme.lua").write_text("-- someone else's install", encoding="utf-8")

        dev.cmd_uninstall()

        assert (target / "keepme.lua").exists()
        assert "left alone" in capsys.readouterr().out

    def test_removes_a_broken_link(self, installed):
        target = dev.target_for(installed, "_retail_")
        target.symlink_to(installed / "gone", target_is_directory=True)

        dev.cmd_uninstall()

        assert not target.is_symlink()

    def test_does_not_delete_the_source(self, installed):
        dev.cmd_install()
        dev.cmd_uninstall()

        assert dev.LINK_SRC.is_dir()
        assert (dev.LINK_SRC / "Libs").is_dir()


class TestStatus:
    def test_reports_each_state(self, installed, capsys):
        dev.link(dev.LINK_SRC, dev.target_for(installed, "_retail_"))
        dev.target_for(installed, "_classic_").symlink_to(installed / "gone")
        real = dev.target_for(installed, "_classic_era_")
        real.mkdir()
        (real / f"{dev.SOURCE_DIR}.toc").write_text("## Version: 1.2.3\n", encoding="utf-8")

        assert dev.cmd_status() == 0

        out = capsys.readouterr().out
        assert "symlink ->" in out
        assert "BROKEN symlink ->" in out
        assert "real directory, version 1.2.3" in out
        assert "not installed" in out


@pytest.fixture
def packaging(tmp_path, monkeypatch):
    """Redirect the packaging paths into tmp and stub out release.sh."""
    calls = []

    def fake_run(command):
        calls.append(command)
        # Stand in for what release.sh -z leaves behind.
        (tmp_path / ".release" / dev.SOURCE_DIR / "Libs" / "AceAddon-3.0").mkdir(parents=True)
        return 0

    monkeypatch.setattr(dev, "BUILD_ROOT", tmp_path / ".release")
    monkeypatch.setattr(dev, "BUILD_LIBS_DIR", tmp_path / ".release" / dev.SOURCE_DIR / "Libs")
    monkeypatch.setattr(dev, "LIBS_DIR", tmp_path / "src" / dev.SOURCE_DIR / "Libs")
    monkeypatch.setattr(dev, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(dev, "require_tool", lambda name: name)
    monkeypatch.setattr(dev, "run", fake_run)

    return calls


class TestLibs:
    def test_fetches_and_copies_into_place(self, packaging):
        assert dev.cmd_libs() == 0

        assert packaging == [["release.sh", "-z"]]
        assert (dev.LIBS_DIR / "AceAddon-3.0").is_dir()

    def test_is_a_no_op_when_libs_are_present(self, packaging, capsys):
        dev.LIBS_DIR.mkdir(parents=True)

        assert dev.cmd_libs() == 0

        assert packaging == [], "should not have shelled out to release.sh"
        assert "already present" in capsys.readouterr().out

    def test_a_failed_fetch_does_not_copy(self, packaging, monkeypatch):
        monkeypatch.setattr(dev, "run", lambda command: 1)

        assert dev.cmd_libs() == 1
        assert not dev.LIBS_DIR.exists()


class TestClean:
    def test_removes_both_trees(self, packaging, capsys):
        (dev.BUILD_ROOT / "junk").mkdir(parents=True)
        (dev.LIBS_DIR / "AceAddon-3.0").mkdir(parents=True)

        assert dev.cmd_clean() == 0

        assert not dev.BUILD_ROOT.exists()
        assert not dev.LIBS_DIR.exists()
        assert "removed" in capsys.readouterr().out

    def test_is_fine_when_there_is_nothing_to_remove(self, packaging):
        assert dev.cmd_clean() == 0

    def test_leaves_the_source_alone(self, packaging):
        (dev.LIBS_DIR / "AceAddon-3.0").mkdir(parents=True)
        source = dev.LIBS_DIR.parent
        (source / "Init.lua").write_text("-- keep me", encoding="utf-8")

        dev.cmd_clean()

        assert (source / "Init.lua").exists()


class TestBuild:
    def test_shells_out_to_the_packager(self, packaging):
        assert dev.cmd_build() == 0
        assert packaging == [["release.sh", "-ze"]]


class TestIsWatched:
    def test_addon_sources_are_watched(self):
        for name in ("Init.lua", "ItemVersion.toc", "Libs.xml"):
            assert dev.is_watched(str(dev.LINK_SRC / name)), name

    def test_nested_sources_are_watched(self):
        assert dev.is_watched(str(dev.LINK_SRC / "Locales" / "deDE.lua"))

    def test_other_extensions_are_not(self):
        for name in ("icon.tga", "notes.md", "ItemVersion.lua.bak", "Init"):
            assert not dev.is_watched(str(dev.LINK_SRC / name)), name

    def test_vendored_libs_are_not_watched(self):
        # The reason the filter exists: Ace3 is large, never edited, and selene
        # skips it anyway.
        assert not dev.is_watched(str(dev.LIBS_DIR / "AceAddon-3.0" / "AceAddon-3.0.lua"))

    def test_the_libs_dir_itself_is_not_watched(self):
        assert not dev.is_watched(str(dev.LIBS_DIR))

    def test_a_lua_file_merely_named_libs_is_watched(self):
        # Libs.xml and a Libs.lua live in the addon root and are ours.
        assert dev.is_watched(str(dev.LINK_SRC / "Libs.lua"))


class TestDescribe:
    def test_names_the_change_and_a_relative_path(self):
        changes = {(dev.Change.modified, str(dev.LINK_SRC / "Init.lua"))}
        assert dev.describe(changes) == ["modified ItemVersion/Init.lua"]

    def test_is_sorted_and_lists_every_change(self):
        # A list, not a set: set iteration order is arbitrary, so a set can land
        # already sorted and let a missing sort() pass unnoticed. This order is
        # reverse-sorted, so it can only pass if the sort really happens.
        changes = [
            (dev.Change.modified, str(dev.LINK_SRC / "Zed.lua")),
            (dev.Change.deleted, str(dev.LINK_SRC / "Mid.lua")),
            (dev.Change.added, str(dev.LINK_SRC / "Init.lua")),
        ]
        assert dev.describe(changes) == [
            "added ItemVersion/Init.lua",
            "deleted ItemVersion/Mid.lua",
            "modified ItemVersion/Zed.lua",
        ]


class TestCli:
    def test_no_command_prints_help(self, capsys):
        assert dev.main([]) == 0
        assert "usage" in capsys.readouterr().out

    def test_bare_help_command_works(self, capsys):
        # Not just --help: CONTRIBUTING tells contributors to run `dev.py help`.
        assert dev.main(["help"]) == 0
        assert "usage" in capsys.readouterr().out

    def test_unknown_command_exits_nonzero(self):
        with pytest.raises(SystemExit) as exit_info:
            dev.main(["nonsense"])
        assert exit_info.value.code != 0

    def test_every_command_is_wired_up(self):
        for name, (handler, help_text) in dev.COMMANDS.items():
            assert callable(handler), name
            assert help_text, name

    def test_die_becomes_exit_one(self, monkeypatch, capsys):
        monkeypatch.delenv("WOW_ROOT", raising=False)
        monkeypatch.setattr(dev, "ENV_FILE", Path("/nonexistent"))

        assert dev.main(["status"]) == 1
        assert "error:" in capsys.readouterr().err


if __name__ == "__main__":
    # Importing dev pulls in watchfiles, and so anyio, before pytest can rewrite
    # the assertions in anyio's plugin. We do not test anyio, so the warning is
    # only noise.
    ignore_anyio = "ignore::pytest.PytestAssertRewriteWarning"
    sys.exit(pytest.main([__file__, "-q", "-W", ignore_anyio, *sys.argv[1:]]))
