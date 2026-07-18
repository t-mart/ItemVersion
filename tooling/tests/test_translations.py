"""Tests for reading, writing and reconciling translations.yml."""

from __future__ import annotations

import pytest  # type: ignore[ty:unresolved-import]

import common
import translations
from translations import Message

SAMPLE = """\
- key: Addon Version
  translations:
    deDE: Addon-Version
- key: Classic|canon
  description: The full name of Classic.
  translations:
    enUS: Classic
- key: Profiles
"""


class TestMessage:
    def test_english_prefers_an_explicit_enus(self):
        message = Message("Classic|canon", None, (("enUS", "Classic"),))
        assert message.english == "Classic"

    def test_english_falls_back_to_the_key(self):
        message = Message("Profiles", None, (("deDE", "Profile"),))
        assert message.english == "Profiles"

    def test_empty_enus_falls_back_to_the_key(self):
        message = Message("Profiles", None, (("enUS", ""),))
        assert message.english == "Profiles"

    def test_has_context(self):
        assert Message("Classic|canon", None, ()).has_context
        assert not Message("Classic", None, ()).has_context


class TestParse:
    def test_reads_every_field(self):
        messages = translations.parse_messages(SAMPLE)
        by_key = {m.key: m for m in messages}

        assert by_key["Addon Version"].by_locale == {"deDE": "Addon-Version"}
        assert by_key["Classic|canon"].description == "The full name of Classic."
        assert by_key["Profiles"].translations == ()

    def test_sorts_by_key_case_insensitively(self):
        text = "- key: zulu\n- key: Alpha\n"
        assert [m.key for m in translations.parse_messages(text)] == ["Alpha", "zulu"]

    def test_empty_file_is_no_messages(self):
        assert translations.parse_messages("") == ()
        assert translations.parse_messages("# just a comment\n") == ()

    def test_a_bad_locale_code_dies(self):
        with pytest.raises(common.Die):
            translations.parse_messages("- key: X\n  translations:\n    german: Hallo\n")

    def test_a_missing_key_dies(self):
        with pytest.raises(common.Die, match="key"):
            translations.parse_messages("- translations:\n    deDE: Hallo\n")

    def test_an_unknown_field_dies(self):
        with pytest.raises(common.Die, match="surprise"):
            translations.parse_messages("- key: X\n  surprise: yes\n")


class TestDump:
    def test_starts_with_the_schema_comment(self):
        out = translations.dump_messages(translations.parse_messages(SAMPLE))
        assert out.splitlines()[0] == translations.SCHEMA_COMMENT

    def test_omits_empty_description_and_translations(self):
        out = translations.dump_messages([Message("Profiles", None, ())])
        assert "description:" not in out
        assert "translations:" not in out

    def test_is_idempotent(self):
        once = translations.dump_messages(translations.parse_messages(SAMPLE))
        twice = translations.dump_messages(translations.parse_messages(once))
        assert once == twice

    def test_round_trips_the_model(self):
        messages = translations.parse_messages(SAMPLE)
        assert translations.parse_messages(translations.dump_messages(messages)) == messages

    def test_keeps_unicode_readable(self):
        out = translations.dump_messages([Message("Cataclysm", None, (("zhCN", "大地的裂变"),))])
        assert "大地的裂变" in out


class TestReconcile:
    MESSAGES = translations.parse_messages(SAMPLE)

    def test_keeps_used_keys_with_their_data(self):
        result = translations.reconcile(self.MESSAGES, ["Classic|canon"])
        assert [m.key for m in result] == ["Classic|canon"]
        assert result[0].description == "The full name of Classic."

    def test_stubs_a_newly_used_key(self):
        result = translations.reconcile(self.MESSAGES, ["Profiles", "Brand New"])
        by_key = {m.key: m for m in result}
        assert by_key["Brand New"] == Message("Brand New", None, ())

    def test_drops_a_key_nothing_uses(self):
        result = translations.reconcile(self.MESSAGES, ["Profiles"])
        assert [m.key for m in result] == ["Profiles"]

    def test_result_is_sorted(self):
        result = translations.reconcile(self.MESSAGES, ["zulu", "Alpha"])
        assert [m.key for m in result] == ["Alpha", "zulu"]


class TestReadWrite:
    def test_missing_file_reads_as_empty(self, tmp_path):
        assert translations.read_messages(tmp_path / "nope.yml") == ()

    def test_write_then_read_round_trips(self, tmp_path):
        path = tmp_path / "translations.yml"
        messages = translations.parse_messages(SAMPLE)
        translations.write_messages(path, messages)
        assert translations.read_messages(path) == messages
