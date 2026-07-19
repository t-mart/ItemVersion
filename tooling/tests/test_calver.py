"""Tests for the calver bump: rendering, parsing, the reset rule, and the command."""

from __future__ import annotations

from datetime import date

import pytest  # type: ignore[ty:unresolved-import]

import calver
import common
import config
from config import Config, VersionConfig

FORMAT = "{YYYY}.{0W}.{N}"

# 2026-07-19 is a Sunday in ISO week 29 of 2026 (isocalendar), so the whole suite
# has a fixed "today" to reason about.
SUNDAY_W29 = date(2026, 7, 19)


class TestRender:
    def test_fills_every_token(self):
        assert calver.render(FORMAT, SUNDAY_W29, 3) == "2026.29.3"

    def test_zero_pads_the_week(self):
        assert calver.render(FORMAT, date(2026, 1, 1), 0) == "2026.01.0"

    def test_uses_the_iso_week_year_not_the_calendar_year(self):
        # 2027-01-01 falls in ISO week 53 of 2026, so the year token is 2026.
        assert calver.render(FORMAT, date(2027, 1, 1), 0) == "2026.53.0"

    def test_an_unknown_token_dies(self):
        with pytest.raises(common.Die, match="unknown token"):
            calver.render("{YYYY}.{MM}.{N}", SUNDAY_W29, 0)


class TestNextVersion:
    def test_same_week_increments_the_serial(self):
        assert calver.next_version(FORMAT, "2026.29.3", SUNDAY_W29) == "2026.29.4"

    def test_a_new_week_resets_the_serial(self):
        # Current version is last week; today is week 29.
        assert calver.next_version(FORMAT, "2026.28.5", SUNDAY_W29) == "2026.29.0"

    def test_a_new_year_resets_the_serial(self):
        assert calver.next_version(FORMAT, "2025.29.2", SUNDAY_W29) == "2026.29.0"

    def test_the_first_bump_of_a_week_is_zero(self):
        assert calver.next_version(FORMAT, "2026.28.0", SUNDAY_W29) == "2026.29.0"

    def test_a_version_that_does_not_fit_the_format_dies(self):
        with pytest.raises(common.Die, match="does not match format"):
            calver.next_version(FORMAT, "v2026-29-3", SUNDAY_W29)

    def test_a_format_without_a_serial_dies(self):
        with pytest.raises(common.Die, match="serial token"):
            calver.next_version("{YYYY}.{0W}", "2026.29", SUNDAY_W29)

    def test_a_format_with_two_serials_dies(self):
        with pytest.raises(common.Die, match="more than one"):
            calver.next_version("{N}.{0W}.{N}", "1.29.3", SUNDAY_W29)

    def test_round_trips_with_render(self):
        # Bumping in the same week, then rendering, is the same string.
        assert calver.next_version(FORMAT, "2026.29.7", SUNDAY_W29) == calver.render(
            FORMAT, SUNDAY_W29, 8
        )


class TestFindVersion:
    def test_reads_the_named_group(self):
        text = "## Title: X\n## Version: 2026.29.3\n"
        value, span = calver.find_version(text, r"## Version: (?P<version>\S+)")
        assert value == "2026.29.3"
        assert text[span[0] : span[1]] == "2026.29.3"

    def test_falls_back_to_the_first_group(self):
        value, _ = calver.find_version("v = 1.2.3", r"v = (\S+)")
        assert value == "1.2.3"

    def test_no_match_dies(self):
        with pytest.raises(common.Die, match="matched nothing"):
            calver.find_version("nothing here", r"## Version: (?P<version>\S+)")

    def test_more_than_one_match_dies(self):
        text = "## Version: 1\n## Version: 2\n"
        with pytest.raises(common.Die, match="matched 2 times"):
            calver.find_version(text, r"## Version: (?P<version>\S+)")

    def test_a_pattern_with_no_group_dies(self):
        with pytest.raises(common.Die, match="capture group"):
            calver.find_version("## Version: 1", r"## Version: \S+")

    def test_invalid_regex_dies(self):
        with pytest.raises(common.Die, match="not valid regex"):
            calver.find_version("anything", r"## Version: (")


class TestCmdBumpCalver:
    @pytest.fixture
    def toc(self, tmp_path, monkeypatch):
        path = tmp_path / "ItemVersion.toc"
        path.write_text("## Title: X\n## Version: 2026.29.3\n## Author: Y\n", encoding="utf-8")

        cfg = Config(
            name="ItemVersion",
            curseforge_project_id=1,
            dev_only=(),
            libs=(("A", "svn://x"),),
            version=VersionConfig(
                file="ItemVersion.toc",
                pattern=r"## Version: (?P<version>\S+)",
                format=FORMAT,
            ),
        )
        monkeypatch.setattr(calver, "load_config", lambda: cfg)
        monkeypatch.setattr(calver, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(common, "REPO_ROOT", tmp_path)
        # Freeze today so the expected bump is stable.
        monkeypatch.setattr(calver, "date", _FixedDate)
        return path

    def test_writes_the_bumped_version(self, toc):
        assert calver.cmd_bump_calver() == 0
        assert "## Version: 2026.29.4\n" in toc.read_text(encoding="utf-8")

    def test_leaves_the_rest_of_the_toc_alone(self, toc):
        calver.cmd_bump_calver()
        text = toc.read_text(encoding="utf-8")
        assert text.startswith("## Title: X\n")
        assert text.endswith("## Author: Y\n")

    def test_dry_run_writes_nothing(self, toc):
        before = toc.read_text(encoding="utf-8")
        assert calver.cmd_bump_calver(dry_run=True) == 0
        assert toc.read_text(encoding="utf-8") == before

    def test_dry_run_says_what_it_would_do(self, toc, capsys):
        calver.cmd_bump_calver(dry_run=True)
        err = capsys.readouterr().err
        assert "would bump" in err
        assert "2026.29.3 -> 2026.29.4" in err

    def test_stdout_is_only_the_new_version(self, toc, capsys):
        # The release workflow captures this into its commit and tag.
        calver.cmd_bump_calver(dry_run=True)
        assert capsys.readouterr().out == "2026.29.4\n"

    def test_a_missing_version_block_dies(self, tmp_path, monkeypatch):
        cfg = Config(name="X", curseforge_project_id=1, dev_only=(), libs=(("A", "svn://x"),))
        monkeypatch.setattr(calver, "load_config", lambda: cfg)
        with pytest.raises(common.Die, match="no `version:` block"):
            calver.cmd_bump_calver()


class _FixedDate(date):
    @classmethod
    def today(cls) -> date:
        return SUNDAY_W29


def test_the_real_config_bumps_from_its_own_toc():
    # The committed wowaddon.yml and TOC must actually drive a bump.
    cfg = config.load_config().require_version_config
    toc_text = (config.REPO_ROOT / cfg.file).read_text(encoding="utf-8")
    current, _ = calver.find_version(toc_text, cfg.pattern)
    # Any date works here; we only assert the pieces line up without raising.
    assert calver.next_version(cfg.format, current, SUNDAY_W29)
