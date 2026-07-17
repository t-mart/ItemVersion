"""Tests for building the TOC's Interface line from Blizzard's endpoints."""

from __future__ import annotations


import pytest  # type: ignore[ty:unresolved-import]

import common
import interfaces
import toc


# A real response from http://us.patch.battle.net:1119/wow/versions, trimmed to
# three regions. Note VersionsName declares its type as "String" while its
# neighbours shout "STRING": nothing here should care about the type at all.


VERSIONS = """\
Region!STRING:0|BuildConfig!HEX:16|CDNConfig!HEX:16|KeyRing!HEX:16|BuildId!DEC:4|VersionsName!String:0|ProductConfig!HEX:16
## seqn = 3880581
us|34a1a445ae41066c7f7a6564892d8bdd|cdd540cf71fba841a296f3c6da69ff30|3ca57fe7319a297346440e4d2a03a0cd|68453|12.0.7.68453|53020d32e1a25648c8e1eafd5771935f
eu|34a1a445ae41066c7f7a6564892d8bdd|cdd540cf71fba841a296f3c6da69ff30|3ca57fe7319a297346440e4d2a03a0cd|68453|12.0.7.68453|53020d32e1a25648c8e1eafd5771935f
cn|34a1a445ae41066c7f7a6564892d8bdd|cdd540cf71fba841a296f3c6da69ff30|3ca57fe7319a297346440e4d2a03a0cd|68453|12.0.7.68453|53020d32e1a25648c8e1eafd5771935f
"""


class TestParseVersions:
    def test_keys_rows_by_column_name(self):
        rows = interfaces.parse_versions(VERSIONS)
        assert rows[0]["Region"] == "us"
        assert rows[0]["VersionsName"] == "12.0.7.68453"
        assert rows[0]["BuildId"] == "68453"

    def test_drops_the_declared_types_from_the_column_names(self):
        assert "VersionsName" in interfaces.parse_versions(VERSIONS)[0]
        assert "VersionsName!String:0" not in interfaces.parse_versions(VERSIONS)[0]

    def test_skips_the_seqn_line(self):
        rows = interfaces.parse_versions(VERSIONS)
        assert len(rows) == 3
        assert all(row["Region"] in ("us", "eu", "cn") for row in rows)

    def test_empty_response_dies(self):
        with pytest.raises(common.Die, match="empty"):
            interfaces.parse_versions("")

    def test_header_with_no_rows_dies(self):
        header = VERSIONS.splitlines()[0]
        with pytest.raises(common.Die, match="no rows"):
            interfaces.parse_versions(header + "\n## seqn = 1\n")

    def test_a_ragged_row_dies(self):
        with pytest.raises(common.Die, match="expected"):
            interfaces.parse_versions(VERSIONS + "us|too|few\n")

    def test_an_html_error_page_dies(self):
        with pytest.raises(common.Die):
            interfaces.parse_versions("<html>502 Bad Gateway</html>")


class TestInterfaceVersion:
    def test_the_four_products_we_ship(self):
        # Checked against the live endpoints and the TOC these produce.
        assert interfaces.interface_version("12.0.7.68453") == "120007"
        assert interfaces.interface_version("5.5.4.68716") == "50504"
        assert interfaces.interface_version("2.5.6.68749") == "20506"
        assert interfaces.interface_version("1.15.8.67156") == "11508"

    def test_pads_minor_and_patch_to_two_digits(self):
        assert interfaces.interface_version("1.2.3.4") == "10203"

    def test_a_two_digit_minor_is_not_padded_further(self):
        assert interfaces.interface_version("1.15.8.67156") == "11508"

    def test_too_few_parts_dies(self):
        with pytest.raises(common.Die, match="cannot read a version"):
            interfaces.interface_version("12.0.7")

    def test_junk_dies(self):
        with pytest.raises(common.Die, match="cannot read a version"):
            interfaces.interface_version("not.a.version.here")


class TestFetchText:
    def test_a_network_error_becomes_a_die(self, monkeypatch):
        def boom(*args, **kwargs):
            raise OSError("Name or service not known")

        monkeypatch.setattr(interfaces.urllib.request, "urlopen", boom)

        # Not an unhandled traceback: the release step reads this.
        with pytest.raises(common.Die, match="could not fetch"):
            interfaces.fetch_text("http://us.patch.battle.net:1119/wow/versions")


class TestInterfaceFor:
    def test_reads_the_requested_region(self, monkeypatch):
        monkeypatch.setattr(interfaces, "fetch_text", lambda url, **kw: VERSIONS)
        assert interfaces.interface_for("wow") == "120007"

    def test_asks_for_the_right_url(self, monkeypatch):
        seen = []
        monkeypatch.setattr(
            interfaces, "fetch_text", lambda url, **kw: seen.append(url) or VERSIONS
        )
        interfaces.interface_for("wow_classic_era")
        assert seen == ["http://us.patch.battle.net:1119/wow_classic_era/versions"]

    def test_a_missing_region_dies(self, monkeypatch):
        monkeypatch.setattr(interfaces, "fetch_text", lambda url, **kw: VERSIONS)
        with pytest.raises(common.Die, match="no zz row"):
            interfaces.interface_for("wow", region="zz")


class TestCmdInterfaces:
    @pytest.fixture
    def stale(self, tmp_path, monkeypatch):
        toc = tmp_path / "ItemVersion.toc"
        toc.write_text("## Title: ItemVersion\n## Interface: 1, 2\n", encoding="utf-8")
        monkeypatch.setattr(interfaces, "TOC_PATH", toc)
        # relative() reports paths against the repo root, so move it here too.
        monkeypatch.setattr(common, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(interfaces, "current_interfaces", lambda: "120007, 50504")
        return toc

    def test_writes_the_new_interfaces(self, stale):
        assert interfaces.cmd_interfaces() == 0
        assert toc.toc_field(stale.read_text(encoding="utf-8"), "Interface") == "120007, 50504"

    def test_dry_run_writes_nothing(self, stale):
        before = stale.read_text(encoding="utf-8")

        assert interfaces.cmd_interfaces(dry_run=True) == 0

        assert stale.read_text(encoding="utf-8") == before

    def test_dry_run_says_what_it_would_write(self, stale, capsys):
        interfaces.cmd_interfaces(dry_run=True)

        err = capsys.readouterr().err
        assert "would update" in err
        assert "1, 2 -> 120007, 50504" in err

    def test_stdout_is_only_the_value(self, stale, capsys):
        # The release workflow captures this into a commit message.
        interfaces.cmd_interfaces(dry_run=True)
        assert capsys.readouterr().out == "120007, 50504\n"

    def test_an_up_to_date_toc_is_left_alone(self, stale, capsys):
        interfaces.cmd_interfaces()
        capsys.readouterr()

        interfaces.cmd_interfaces()

        assert "already lists" in capsys.readouterr().err


class TestCurrentInterfaces:
    def test_joins_every_product_in_order(self, monkeypatch):
        monkeypatch.setattr(interfaces, "interface_for", lambda product, region: {
            "wow": "120007",
            "wow_classic": "50504",
            "wow_anniversary": "20506",
            "wow_classic_era": "11508",
        }[product])

        assert interfaces.current_interfaces() == "120007, 50504, 20506, 11508"

    def test_covers_the_products_the_toc_lists(self):
        # The TOC and WOW_PRODUCTS have to stay the same length, or the Interface
        # line silently loses a flavor.
        listed = toc.toc_field(
            interfaces.TOC_PATH.read_text(encoding="utf-8"), "Interface"
        )
        assert listed is not None
        assert len(listed.split(",")) == len(interfaces.WOW_PRODUCTS)
