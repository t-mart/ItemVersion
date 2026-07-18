"""Tests for reading and writing the TOC's header fields."""

from __future__ import annotations


import pytest  # type: ignore[ty:unresolved-import]

import common
import config
import toc


class TestSetTocField:
    TOC = "## Title: ItemVersion\n## Interface: 1, 2\n## Author: Tim Martin\n"

    def test_replaces_the_value(self):
        assert toc.set_toc_field(self.TOC, "Interface", "3, 4") == (
            "## Title: ItemVersion\n## Interface: 3, 4\n## Author: Tim Martin\n"
        )

    def test_leaves_every_other_line_alone(self):
        updated = toc.set_toc_field(self.TOC, "Interface", "3, 4")
        assert "## Title: ItemVersion" in updated
        assert "## Author: Tim Martin" in updated
        assert len(updated.splitlines()) == len(self.TOC.splitlines())

    def test_round_trips_with_the_reader(self):
        updated = toc.set_toc_field(self.TOC, "Interface", "120007, 50504")
        assert toc.toc_field(updated, "Interface") == "120007, 50504"

    def test_a_missing_field_dies(self):
        with pytest.raises(common.Die, match="Nonsense"):
            toc.set_toc_field(self.TOC, "Nonsense", "x")

    def test_the_real_toc_has_an_interface_line(self):
        text = config.load_config().toc_path.read_text(encoding="utf-8")
        value = toc.toc_field(text, "Interface")
        assert value, "the shipped TOC must list interface versions"
        assert all(part.strip().isdigit() for part in value.split(","))


class TestLocaleBlock:
    TOC = (
        "## Title: X\n\n"
        "Libs.xml\n"
        "Locales\\enUS.lua\n"
        "Locales\\deDE.lua\n"
        "Init.lua\n"
    )

    def test_reads_the_locale_codes(self):
        assert toc.toc_locales(self.TOC) == ["enUS", "deDE"]

    def test_reads_forward_slashes_too(self):
        assert toc.toc_locales("Locales/enUS.lua\nLocales/frFR.lua\n") == ["enUS", "frFR"]

    def test_rewrites_the_block_in_place(self):
        out = toc.set_toc_locales(self.TOC, ["enUS", "frFR", "koKR"])
        assert toc.toc_locales(out) == ["enUS", "frFR", "koKR"]
        # Everything around the block is left exactly as it was.
        assert "Libs.xml\n" in out
        assert out.endswith("Init.lua\n")

    def test_shrinking_the_block_drops_lines(self):
        out = toc.set_toc_locales(self.TOC, ["enUS"])
        assert toc.toc_locales(out) == ["enUS"]
        assert "deDE" not in out

    def test_round_trips_with_the_reader(self):
        for want in (["enUS"], ["enUS", "deDE", "zhCN"]):
            assert toc.toc_locales(toc.set_toc_locales(self.TOC, want)) == want

    def test_preserves_crlf(self):
        crlf = self.TOC.replace("\n", "\r\n")
        out = toc.set_toc_locales(crlf, ["enUS"])
        assert "Locales\\enUS.lua\r\n" in out

    def test_no_block_dies(self):
        with pytest.raises(common.Die, match="no Locales"):
            toc.set_toc_locales("## Title: X\n\nInit.lua\n", ["enUS"])

    def test_non_contiguous_block_dies(self):
        scattered = "Locales\\enUS.lua\nInit.lua\nLocales\\deDE.lua\n"
        with pytest.raises(common.Die, match="contiguous"):
            toc.set_toc_locales(scattered, ["enUS", "deDE"])


class TestVersionFromToc:
    def test_reads_the_version(self):
        assert toc.version_from_toc("## Title: X\n## Version: 2026.28.0\n") == "2026.28.0"

    def test_missing_version_is_none(self):
        assert toc.version_from_toc("## Title: X\n") is None

    def test_ignores_a_version_further_in(self):
        assert toc.version_from_toc("## X-Foo: ## Version: nope\n") is None
