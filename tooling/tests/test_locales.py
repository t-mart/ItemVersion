"""Tests for the locale tool: scanning usage, checking, and generating Lua.

A checker that reports nothing is indistinguishable from a checker that is broken,
so most of these feed it a known-bad input and assert it complains.
"""

from __future__ import annotations

from pathlib import Path

import pytest  # type: ignore[ty:unresolved-import]

import config
import locales
import translations
from config import Config
from translations import Message

PATH = Path("translations.yml")


class TestSpecifiers:
    def test_finds_specifiers_in_order(self):
        assert locales.specifiers("%s held %d times") == sorted(["%s", "%d"])

    def test_escaped_percent_is_not_a_specifier(self):
        assert locales.specifiers("100%% sure") == []

    def test_width_and_precision(self):
        assert locales.specifiers("%.2f and %-5s") == sorted(["%.2f", "%-5s"])

    def test_bare_string_has_none(self):
        assert locales.specifiers("Addon Version") == []


class TestTokens:
    def test_finds_tokens(self):
        assert locales.tokens("Added in {expacIcon} ({versionTriple})") == {
            "expacIcon",
            "versionTriple",
        }

    def test_no_tokens(self):
        assert locales.tokens("Profiles") == set()


class TestUsages:
    def test_finds_key_and_location(self, tmp_path):
        path = tmp_path / "Thing.lua"
        path.write_text('local x = L["Profiles"]\n', encoding="utf-8")
        used, problems = locales.find_usages([path])
        assert set(used) == {"Profiles"}
        assert problems == []
        assert used["Profiles"] == ["Thing.lua:1"]

    def test_computed_index_warns_rather_than_crashes(self, tmp_path):
        """p3lim's scanner raises AttributeError here. We must not."""
        path = tmp_path / "Thing.lua"
        path.write_text("local x = L[a .. b]\n", encoding="utf-8")
        used, problems = locales.find_usages([path])
        assert used == {}
        assert [p.severity for p in problems] == [locales.WARNING]
        assert "cannot verify" in problems[0].message

    def test_ignores_other_tables(self, tmp_path):
        path = tmp_path / "Thing.lua"
        path.write_text('local x = NotL["Profiles"]\n', encoding="utf-8")
        used, _ = locales.find_usages([path])
        assert used == {}

    def test_ignores_commented_and_quoted_text(self, tmp_path):
        """The false positives a regex would happily report."""
        path = tmp_path / "Thing.lua"
        path.write_text('-- L["Commented"]\nlocal s = \'L["Quoted"]\'\n', encoding="utf-8")
        used, _ = locales.find_usages([path])
        assert used == {}

    def test_single_quoted_key_is_found(self, tmp_path):
        path = tmp_path / "Thing.lua"
        path.write_text("local x = L['Profiles']\n", encoding="utf-8")
        used, _ = locales.find_usages([path])
        assert set(used) == {"Profiles"}

    def test_unparseable_file_is_an_error(self, tmp_path):
        path = tmp_path / "Broken.lua"
        path.write_text("this is not ) lua (", encoding="utf-8")
        _, problems = locales.find_usages([path])
        assert [p.severity for p in problems] == [locales.ERROR]


class TestSourceFiles:
    def test_skips_locales_libs_and_data(self, tmp_path):
        addon = tmp_path / "ItemVersion"
        (addon / "Locales").mkdir(parents=True)
        (addon / "Libs" / "Ace").mkdir(parents=True)
        (addon / "Locales" / "enUS.lua").write_text("-- x", encoding="utf-8")
        (addon / "Libs" / "Ace" / "Ace.lua").write_text("-- x", encoding="utf-8")
        (addon / "ItemData.lua").write_text("-- x", encoding="utf-8")
        (addon / "Init.lua").write_text("-- x", encoding="utf-8")

        found = {p.name for p in locales.source_files(addon)}
        assert found == {"Init.lua"}


class TestChecks:
    def test_empty_value_is_an_error(self):
        problems = locales.check_empty(Message("Profiles", None, (("deDE", ""),)), PATH)
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "empty deDE" in problems[0].message

    def test_a_real_translation_is_not_empty(self):
        assert locales.check_empty(Message("Profiles", None, (("deDE", "Profile"),)), PATH) == []

    def test_context_key_without_english_is_an_error(self):
        problems = locales.check_context(Message("Legion|canon", None, ()), PATH)
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "context marker" in problems[0].message

    def test_context_key_with_english_passes(self):
        message = Message("Legion|canon", None, (("enUS", "Legion"),))
        assert locales.check_context(message, PATH) == []

    def test_ordinary_key_needs_no_english(self):
        assert locales.check_context(Message("Profiles", None, ()), PATH) == []

    def test_dropped_specifier_is_an_error(self):
        message = Message("Found %d items", None, (("deDE", "Nichts gefunden"),))
        problems = locales.check_placeholders(message, PATH)
        assert "placeholder mismatch" in problems[0].message

    def test_changed_specifier_type_is_an_error(self):
        message = Message("Found %d items", None, (("deDE", "Fur %s"),))
        assert len(locales.check_placeholders(message, PATH)) == 1

    def test_misspelled_token_is_an_error(self):
        message = Message(
            "Added in {expacIcon}", None, (("deDE", "Hinzugefugt in {expacIcone}"),)
        )
        problems = locales.check_placeholders(message, PATH)
        assert "expacIcon" in problems[0].message

    def test_matching_placeholders_pass(self):
        message = Message("Added in {expacIcon}", None, (("deDE", "In {expacIcon}"),))
        assert locales.check_placeholders(message, PATH) == []

    def test_reordered_specifiers_pass(self):
        """Word order changes between languages. Only the multiset matters."""
        message = Message("%s and %s", None, (("deDE", "%s und %s"),))
        assert locales.check_placeholders(message, PATH) == []

    def test_placeholders_checked_against_an_explicit_english(self):
        # english is the enUS value here, not the key, so the token must match it.
        message = Message(
            "greeting", None, (("enUS", "Hi {name}"), ("deDE", "Hallo {nom}"))
        )
        problems = locales.check_placeholders(message, PATH)
        assert any("token mismatch" in p.message for p in problems)

    def test_empty_value_is_skipped_by_placeholders(self):
        message = Message("Found %d items", None, (("deDE", ""),))
        assert locales.check_placeholders(message, PATH) == []

    def test_duplicate_key_is_an_error(self):
        messages = (Message("BfA", None, ()), Message("BfA", None, ()))
        problems = locales.check_duplicates(messages, PATH)
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "duplicate" in problems[0].message

    def test_used_but_undefined_is_an_error(self):
        problems = locales.check_usage((), {"Ghost": ["Thing.lua:1"]}, PATH)
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "does not define it" in problems[0].message

    def test_defined_but_unused_is_an_error(self):
        problems = locales.check_usage((Message("Orphan", None, ()),), {}, PATH)
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "nothing uses it" in problems[0].message

    def test_canonical_text_passes(self):
        text = translations.dump_messages([Message("Alpha", None, ()), Message("Beta", None, ())])
        assert locales.check_canonical(text, PATH) == []

    def test_unsorted_text_fails_canonical(self):
        text = "- key: Zulu\n- key: Alpha\n"
        problems = locales.check_canonical(text, PATH)
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "canonical" in problems[0].message


class TestLocalesIn:
    def test_default_first_then_sorted_others(self):
        messages = (
            Message("A", None, (("zhCN", "x"), ("deDE", "y"))),
            Message("B", None, (("deDE", "z"),)),
        )
        assert locales.locales_in(messages) == ["enUS", "deDE", "zhCN"]

    def test_a_locale_with_only_empty_values_is_excluded(self):
        messages = (Message("A", None, (("deDE", ""),)),)
        assert locales.locales_in(messages) == ["enUS"]


class TestRenderLocale:
    def test_default_uses_true_for_plain_keys(self):
        out = locales.render_locale((Message("Profiles", None, ()),), "enUS")
        assert 'L["Profiles"] = true' in out
        assert 'NewLocale(AddonName, "enUS", true)' in out

    def test_default_spells_out_a_context_key(self):
        messages = (Message("Legion|canon", None, (("enUS", "Legion"),)),)
        out = locales.render_locale(messages, "enUS")
        assert 'L["Legion|canon"] = "Legion"' in out
        assert 'L["Legion|canon"] = true' not in out

    def test_other_locale_only_lists_translated_keys(self):
        messages = (
            Message("Alpha", None, (("deDE", "Alfa"),)),
            Message("Beta", None, ()),
        )
        out = locales.render_locale(messages, "deDE")
        assert 'L["Alpha"] = "Alfa"' in out
        assert "Beta" not in out
        assert 'NewLocale(AddonName, "deDE")' in out
        assert ", true)" not in out

    def test_banner_warns_against_editing(self):
        out = locales.render_locale((Message("A", None, ()),), "enUS")
        assert out.startswith("-- Generated")

    def test_output_is_sorted(self):
        messages = (Message("Zulu", None, ()), Message("Alpha", None, ()))
        out = locales.render_locale(messages, "enUS")
        assert out.index('L["Alpha"]') < out.index('L["Zulu"]')

    def test_quotes_are_escaped(self):
        assert locales.lua_quote('a"b') == '"a\\"b"'


class TestCoverage:
    def test_counts_only_real_translations_per_locale(self):
        messages = (
            Message("A", None, (("deDE", "x"), ("zhCN", "y"))),
            Message("B", None, (("deDE", "z"),)),
            Message("C", None, ()),
        )
        assert locales.coverage(messages) == {"deDE": 2, "zhCN": 1}


@pytest.fixture
def tree(tmp_path, monkeypatch):
    """A scratch addon: source that uses two keys, a matching translations.yml,
    and a TOC whose locale block already lists what the source implies."""
    monkeypatch.setattr(config, "SRC_ROOT", tmp_path / "src")
    cfg = Config(name="ItemVersion", curseforge_project_id=1, ignore=(), libs=(("A", "svn://x"),))

    cfg.source_dir.mkdir(parents=True)
    (cfg.source_dir / "Thing.lua").write_text(
        'print(L["Alpha"])\nprint(L["Beta"])\n', encoding="utf-8"
    )
    cfg.toc_path.write_text(
        "## Title: ItemVersion\n\nLocales\\enUS.lua\nLocales\\deDE.lua\nThing.lua\n",
        encoding="utf-8",
    )
    messages = (Message("Alpha", None, (("deDE", "Alfa"),)), Message("Beta", None, ()))
    translations.write_messages(cfg.translations_path, messages)

    monkeypatch.setattr(locales, "load_config", lambda: cfg)
    return cfg


class TestCheckTocLocales:
    def test_matching_toc_passes(self, tree):
        messages = translations.read_messages(tree.translations_path)
        assert locales.check_toc_locales(tree, messages) == []

    def test_drifted_toc_is_an_error(self, tree):
        # Drop deDE from the source so the TOC now over-lists.
        translations.write_messages(tree.translations_path, [Message("Alpha", None, ())])
        messages = translations.read_messages(tree.translations_path)
        problems = locales.check_toc_locales(tree, messages)
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "run ./dev prepare-src" in problems[0].message


class TestGenerate:
    def test_writes_default_and_translated_locales(self, tree):
        written = locales.generate(tree)

        names = {p.name for p in written}
        assert names == {"enUS.lua", "deDE.lua"}
        enus = (tree.locales_dir / "enUS.lua").read_text(encoding="utf-8")
        assert 'L["Alpha"] = true' in enus and 'L["Beta"] = true' in enus
        dede = (tree.locales_dir / "deDE.lua").read_text(encoding="utf-8")
        assert 'L["Alpha"] = "Alfa"' in dede and "Beta" not in dede

    def test_removes_a_stale_locale_file(self, tree):
        tree.locales_dir.mkdir(parents=True)
        (tree.locales_dir / "frFR.lua").write_text("-- left over", encoding="utf-8")

        locales.generate(tree)

        assert not (tree.locales_dir / "frFR.lua").exists()

    def test_syncs_a_new_locale_into_the_toc(self, tree):
        messages = (
            Message("Alpha", None, (("deDE", "Alfa"), ("frFR", "Alfa"))),
            Message("Beta", None, ()),
        )
        translations.write_messages(tree.translations_path, messages)

        locales.generate(tree)

        from toc import toc_locales

        assert toc_locales(tree.toc_path.read_text(encoding="utf-8")) == ["enUS", "deDE", "frFR"]


class TestMain:
    def test_clean_tree_passes(self, tree, capsys):
        assert locales.main(["--check"]) == 0
        out = capsys.readouterr().out
        assert "0 error(s)" in out
        assert "1/2 translated" in out

    def test_check_writes_nothing(self, tree):
        before = tree.translations_path.read_text(encoding="utf-8")
        locales.main(["--check"])
        assert tree.translations_path.read_text(encoding="utf-8") == before

    def test_used_but_undefined_fails(self, tree, capsys):
        (tree.source_dir / "Thing.lua").write_text('print(L["Ghost"])\n', encoding="utf-8")
        assert locales.main(["--check"]) == 1
        assert "does not define it" in capsys.readouterr().out

    def test_fix_stubs_a_new_key(self, tree):
        (tree.source_dir / "Thing.lua").write_text(
            'print(L["Alpha"])\nprint(L["Beta"])\nprint(L["Gamma"])\n', encoding="utf-8"
        )
        assert locales.main([]) == 0
        keys = [m.key for m in translations.read_messages(tree.translations_path)]
        assert "Gamma" in keys

    def test_fix_drops_an_unused_key(self, tree):
        messages = translations.read_messages(tree.translations_path)
        translations.write_messages(
            tree.translations_path, [*messages, Message("Orphan", None, ())]
        )
        # It is defined but unused, so check fails first.
        assert locales.main(["--check"]) == 1

        assert locales.main([]) == 0
        keys = [m.key for m in translations.read_messages(tree.translations_path)]
        assert "Orphan" not in keys

    def test_fix_rewrites_a_noncanonical_file(self, tree):
        # Unsorted and missing the schema comment, but the deDE stays so the TOC's
        # locale list still matches.
        tree.translations_path.write_text(
            "- key: Beta\n- key: Alpha\n  translations:\n    deDE: Alfa\n", encoding="utf-8"
        )
        assert locales.main([]) == 0
        text = tree.translations_path.read_text(encoding="utf-8")
        assert text.splitlines()[0] == translations.SCHEMA_COMMENT
        assert text.index("Alpha") < text.index("Beta")

    def test_bad_placeholder_fails(self, tree, capsys):
        (tree.source_dir / "Thing.lua").write_text('print(L["Hit %d"])\n', encoding="utf-8")
        translations.write_messages(
            tree.translations_path, [Message("Hit %d", None, (("deDE", "%s mal"),))]
        )
        # Line up the TOC so only the placeholder is wrong.
        tree.toc_path.write_text(
            "## Title: ItemVersion\n\nLocales\\enUS.lua\nLocales\\deDE.lua\nThing.lua\n",
            encoding="utf-8",
        )
        assert locales.main(["--check"]) == 1
        assert "placeholder mismatch" in capsys.readouterr().out

    def test_check_does_not_paper_over_a_problem(self, tree):
        messages = translations.read_messages(tree.translations_path)
        translations.write_messages(
            tree.translations_path, [*messages, Message("Orphan", None, ())]
        )
        locales.main(["--check"])
        assert "Orphan" in tree.translations_path.read_text(encoding="utf-8")
