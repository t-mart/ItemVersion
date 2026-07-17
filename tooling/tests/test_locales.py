"""Tests for the locale checker.

  ./dev test

A checker that reports nothing is indistinguishable from a checker that is
broken, so most of these feed it a known-bad file and assert it complains.
"""

from __future__ import annotations

from pathlib import Path

import pytest  # type: ignore[ty:unresolved-import]

import locales


def locale_from(tmp_path: Path, name: str, text: str) -> locales.LocaleFile:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    result = locales.read_locale(path)
    assert isinstance(result, locales.LocaleFile), result
    return result


DEUTSCH_HEADER = """\
local AddonName = ...
local L = LibStub("AceLocale-3.0"):NewLocale(AddonName, "deDE")
if not L then
  return
end
"""


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


class TestParsing:
    def test_reads_true_as_none_value(self, tmp_path):
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["BfA"] = true\n')
        assert loc.by_key["BfA"].value is None
        assert loc.by_key["BfA"].is_noop

    def test_single_quoted_key_is_found(self, tmp_path):
        """The case a regex over L["..."] would miss outright."""
        loc = locale_from(
            tmp_path, "deDE.lua", DEUTSCH_HEADER + "L['Profiles'] = 'Profile'\n"
        )
        assert loc.by_key["Profiles"].value == "Profile"

    def test_escaped_quote_in_key(self, tmp_path):
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["a\\"b"] = "c"\n')
        assert 'a"b' in loc.by_key

    def test_unicode_round_trips(self, tmp_path):
        loc = locale_from(
            tmp_path, "ruRU.lua", 'L = L or {}\nL["Description"] = "Описание"\n'
        )
        assert loc.by_key["Description"].value == "Описание"

    def test_declared_locale_beats_filename(self, tmp_path):
        loc = locale_from(
            tmp_path, "whatever.lua", DEUTSCH_HEADER + 'L["BfA"] = true\n'
        )
        assert loc.locale == "deDE"
        assert not loc.is_default

    def test_default_locale_detected(self, tmp_path):
        text = 'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\nL["BfA"] = true\n'
        loc = locale_from(tmp_path, "enUS.lua", text)
        assert loc.is_default

    def test_export_format_falls_back_to_filename(self, tmp_path):
        """A raw CurseForge export has no NewLocale call at all."""
        loc = locale_from(tmp_path, "zhCN.lua", 'L = L or {}\nL["BfA"] = true\n')
        assert loc.locale == "zhCN"
        assert not loc.is_default

    def test_header_is_not_kept_from_the_file(self, tmp_path):
        """Nothing above the entries is read back; render rebuilds it."""
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["BfA"] = true\n')
        assert not hasattr(loc, "header")


class TestNoop:
    def test_value_echoing_key_is_noop(self, tmp_path):
        loc = locale_from(
            tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Legion"] = "Legion"\n'
        )
        assert loc.by_key["Legion"].is_noop

    def test_real_translation_is_not_noop(self, tmp_path):
        loc = locale_from(
            tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Profiles"] = "Profile"\n'
        )
        assert not loc.by_key["Profiles"].is_noop


class TestPlaceholders:
    def test_dropped_specifier_is_an_error(self, tmp_path):
        key = "No version information found for item ID %d"
        loc = locale_from(
            tmp_path, "deDE.lua", DEUTSCH_HEADER + f'L["{key}"] = "Nichts gefunden"\n'
        )
        problems = locales.check_placeholders(loc, {key})
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "placeholder mismatch" in problems[0].message

    def test_changed_specifier_type_is_an_error(self, tmp_path):
        key = "No version information found for item ID %d"
        loc = locale_from(
            tmp_path, "deDE.lua", DEUTSCH_HEADER + f'L["{key}"] = "Nichts fur %s"\n'
        )
        problems = locales.check_placeholders(loc, {key})
        assert len(problems) == 1

    def test_misspelled_token_is_an_error(self, tmp_path):
        key = "Added in {expacIcon} ({versionTriple})"
        text = (
            DEUTSCH_HEADER
            + f'L["{key}"] = "Hinzugefugt in {{expacIcone}} ({{versionTriple}})"\n'
        )
        loc = locale_from(tmp_path, "deDE.lua", text)
        problems = locales.check_placeholders(loc, {key})
        assert len(problems) == 1
        assert "expacIcon" in problems[0].message

    def test_matching_placeholders_pass(self, tmp_path):
        key = "Added in {expacIcon} ({versionTriple})"
        text = (
            DEUTSCH_HEADER
            + f'L["{key}"] = "Hinzugefugt in {{expacIcon}} ({{versionTriple}})"\n'
        )
        loc = locale_from(tmp_path, "deDE.lua", text)
        assert locales.check_placeholders(loc, {key}) == []

    def test_reordered_specifiers_pass(self, tmp_path):
        """Word order changes between languages. Only the multiset matters."""
        key = "%s and %s"
        loc = locale_from(
            tmp_path, "deDE.lua", DEUTSCH_HEADER + f'L["{key}"] = "%s und %s"\n'
        )
        assert locales.check_placeholders(loc, {key}) == []

    def test_true_value_is_skipped(self, tmp_path):
        key = "No version information found for item ID %d"
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + f'L["{key}"] = true\n')
        assert locales.check_placeholders(loc, {key}) == []


class TestStructure:
    def test_duplicate_key_is_an_error(self, tmp_path):
        text = DEUTSCH_HEADER + 'L["BfA"] = "A"\nL["BfA"] = "B"\n'
        loc = locale_from(tmp_path, "deDE.lua", text)
        problems = locales.check_duplicates(loc)
        assert len(problems) == 1
        assert "duplicate" in problems[0].message

    def test_unknown_key_is_an_error(self, tmp_path):
        loc = locale_from(
            tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Nonsense"] = "X"\n'
        )
        problems = locales.check_unknown_keys(loc, {"BfA"})
        assert len(problems) == 1
        assert "not in enUS" in problems[0].message

    def test_unsorted_is_a_warning(self, tmp_path):
        text = DEUTSCH_HEADER + 'L["Zulu"] = "Z"\nL["Alpha"] = "A"\n'
        loc = locale_from(tmp_path, "deDE.lua", text)
        assert [p.severity for p in locales.check_sorted(loc)] == [locales.WARNING]

    def test_sorted_passes(self, tmp_path):
        text = DEUTSCH_HEADER + 'L["Alpha"] = "A"\nL["Zulu"] = "Z"\n'
        loc = locale_from(tmp_path, "deDE.lua", text)
        assert locales.check_sorted(loc) == []

    def test_sort_is_case_insensitive(self):
        """The order the existing enUS block is already in.

        These four discriminate: a case-sensitive sort puts every uppercase
        letter before every lowercase one, so it would yield WoD, WoW Build,
        World of Warcraft, WotLK.
        """
        keys = ["WoD", "World of Warcraft", "WotLK", "WoW Build"]
        assert sorted(keys, key=locales.sort_key) == keys
        assert sorted(keys) != keys


class TestEmptyValues:
    def test_half_finished_stub_is_an_error(self, tmp_path):
        """Uncommenting a stub without filling it in blanks the string."""
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Profiles"] = ""\n')
        problems = locales.check_empty_values(loc)
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "nothing at all" in problems[0].message

    def test_a_real_translation_passes(self, tmp_path):
        loc = locale_from(
            tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Profiles"] = "Profile"\n'
        )
        assert locales.check_empty_values(loc) == []

    def test_a_commented_stub_is_not_an_entry(self, tmp_path):
        """The stub as written by the tool must not trip this check."""
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + '-- L["Profiles"] = ""\n')
        assert locales.check_empty_values(loc) == []

    def test_true_is_not_empty(self, tmp_path):
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Profiles"] = true\n')
        assert locales.check_empty_values(loc) == []


class TestContextKeys:
    def test_true_on_a_context_key_is_an_error(self, tmp_path):
        """`= true` would put the marker itself in front of a player."""
        text = (
            'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\n'
            'L["Legion|canon"] = true\n'
        )
        loc = locale_from(tmp_path, "enUS.lua", text)
        problems = locales.check_context_keys(loc)
        assert [p.severity for p in problems] == [locales.ERROR]
        assert "would display the marker" in problems[0].message

    def test_explicit_english_on_a_context_key_passes(self, tmp_path):
        text = (
            'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\n'
            'L["Legion|canon"] = "Legion"\n'
        )
        loc = locale_from(tmp_path, "enUS.lua", text)
        assert locales.check_context_keys(loc) == []

    def test_true_on_an_ordinary_key_is_fine(self, tmp_path):
        text = (
            'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\n'
            'L["Profiles"] = true\n'
        )
        loc = locale_from(tmp_path, "enUS.lua", text)
        assert locales.check_context_keys(loc) == []

    def test_render_keeps_an_explicit_enUS_value(self, tmp_path):
        """Rendering enUS must not flatten a context key back to `= true`."""
        text = (
            'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\n'
            'L["Legion|canon"] = "Legion"\n'
            'L["Profiles"] = true\n'
        )
        loc = locale_from(tmp_path, "enUS.lua", text)
        out = locales.render(loc, {"Legion|canon", "Profiles"})
        assert 'L["Legion|canon"] = "Legion"' in out
        assert 'L["Profiles"] = true' in out
        assert 'L["Legion|canon"] = true' not in out

    def test_two_contexts_of_one_word_can_differ(self, tmp_path):
        """The whole point: one English word, two independent translations."""
        text = DEUTSCH_HEADER + 'L["Legion|canon"] = "Legion"\nL["Legion|short"] = "Leg"\n'
        loc = locale_from(tmp_path, "deDE.lua", text)
        assert loc.by_key["Legion|canon"].value == "Legion"
        assert loc.by_key["Legion|short"].value == "Leg"


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
        path.write_text(
            '-- L["Commented"]\nlocal s = \'L["Quoted"]\'\n', encoding="utf-8"
        )
        used, _ = locales.find_usages([path])
        assert used == {}

    def test_unparseable_file_is_an_error(self, tmp_path):
        path = tmp_path / "Broken.lua"
        path.write_text("this is not ) lua (", encoding="utf-8")
        _, problems = locales.find_usages([path])
        assert [p.severity for p in problems] == [locales.ERROR]


class TestRender:
    def test_missing_keys_become_commented_stubs(self, tmp_path):
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Alpha"] = "A"\n')
        reference = {"Alpha", "Zulu"}
        out = locales.render(loc, reference)
        assert 'L["Alpha"] = "A"' in out
        assert '-- L["Zulu"] = ""' in out

    def test_noop_entries_are_demoted_to_stubs(self, tmp_path):
        """`= true` in a non-default locale says nothing the fallback would not."""
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Alpha"] = true\n')
        out = locales.render(loc, {"Alpha"})
        assert '-- L["Alpha"] = ""' in out

    def test_header_is_generated_from_the_locale(self, tmp_path):
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Alpha"] = "A"\n')
        out = locales.render(loc, {"Alpha"})
        assert out.startswith(locales.header_for("deDE", False))
        assert 'NewLocale(AddonName, "deDE")' in out
        assert "if not L then" in out

    def test_export_format_header_is_replaced(self, tmp_path):
        """A CurseForge export leaks a global L. Rendering it fixes that."""
        loc = locale_from(tmp_path, "zhCN.lua", 'L = L or {}\nL["Alpha"] = "A"\n')
        out = locales.render(loc, {"Alpha"})
        assert "L = L or {}" not in out
        assert 'local L = LibStub("AceLocale-3.0"):NewLocale(AddonName, "zhCN")' in out

    def test_default_locale_header_passes_isDefault(self, tmp_path):
        text = 'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\nL["Alpha"] = true\n'
        loc = locale_from(tmp_path, "enUS.lua", text)
        out = locales.render(loc, {"Alpha"})
        assert 'NewLocale(AddonName, "enUS", true)' in out

    def test_output_is_sorted(self, tmp_path):
        text = DEUTSCH_HEADER + 'L["Zulu"] = "Z"\nL["Alpha"] = "A"\n'
        loc = locale_from(tmp_path, "deDE.lua", text)
        out = locales.render(loc, {"Alpha", "Zulu"})
        assert out.index('L["Alpha"]') < out.index('L["Zulu"]')

    def test_render_is_idempotent(self, tmp_path):
        """A stub must not parse as an entry, or a second run would churn."""
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Alpha"] = "A"\n')
        reference = {"Alpha", "Zulu"}

        once = locales.render(loc, reference)
        again = locales.render(locale_from(tmp_path, "deDE.lua", once), reference)

        assert once == again

    def test_idempotent_when_the_first_key_is_a_stub(self, tmp_path):
        """The stub sorts above every real entry here.

        A header rule based on the first *entry* swallows that stub, then
        re-emits it below, and the file grows by one line every run.
        """
        loc = locale_from(tmp_path, "deDE.lua", DEUTSCH_HEADER + 'L["Zulu"] = "Z"\n')
        reference = {"Alpha", "Zulu"}

        once = locales.render(loc, reference)
        again = locales.render(locale_from(tmp_path, "deDE.lua", once), reference)

        assert once == again
        assert once.count('-- L["Alpha"] = ""') == 1
        assert once.startswith(locales.header_for("deDE", False))

    def test_stubs_do_not_accumulate_over_many_runs(self, tmp_path):
        """The real-world shape: a locale with only a handful translated."""
        reference = {"Alpha", "Beta", "Gamma", "Zulu"}
        text = DEUTSCH_HEADER + 'L["Zulu"] = "Z"\n'

        for _ in range(4):
            text = locales.render(locale_from(tmp_path, "deDE.lua", text), reference)

        assert text.count('-- L["Alpha"] = ""') == 1
        assert text.count('L["Zulu"] = "Z"') == 1
        entry_lines = [ln for ln in text.splitlines() if "L[" in ln]
        assert len(entry_lines) == len(reference)

    def test_default_locale_renders_true(self, tmp_path):
        text = 'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\nL["Alpha"] = true\n'
        loc = locale_from(tmp_path, "enUS.lua", text)
        out = locales.render(loc, {"Alpha"})
        assert 'L["Alpha"] = true' in out

    def test_quotes_are_escaped(self):
        assert locales.lua_quote('a"b') == '"a\\"b"'


class TestCoverage:
    def test_counts_only_real_translations(self, tmp_path):
        text = (
            DEUTSCH_HEADER
            + 'L["Alpha"] = "A"\nL["Beta"] = true\nL["Gamma"] = "Gamma"\n'
        )
        loc = locale_from(tmp_path, "deDE.lua", text)
        assert locales.coverage(loc, {"Alpha", "Beta", "Gamma"}) == (1, 3)


class TestEndToEnd:
    """Drive main() against a scratch tree, the way CI and a developer would."""

    @pytest.fixture
    def tree(self, tmp_path):
        addon = tmp_path / "src/ItemVersion"
        (addon / "Locales").mkdir(parents=True)
        (addon / "Locales" / "enUS.lua").write_text(
            'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\n'
            'L["Alpha"] = true\n'
            'L["Beta"] = true\n',
            encoding="utf-8",
        )
        (addon / "Thing.lua").write_text(
            'print(L["Alpha"])\nprint(L["Beta"])\n', encoding="utf-8"
        )
        (addon / "Locales" / "deDE.lua").write_text(
            DEUTSCH_HEADER + 'L["Alpha"] = "Alfa"\n', encoding="utf-8"
        )
        return tmp_path

    def run(self, tree, *extra):
        return locales.main(["--root", str(tree), *extra])

    def test_clean_tree_passes(self, tree, capsys):
        assert self.run(tree, "--check") == 0
        assert "1/2 translated" in capsys.readouterr().out

    def test_check_mode_writes_nothing(self, tree):
        before = (tree / "src/ItemVersion/Locales/deDE.lua").read_text(encoding="utf-8")
        self.run(tree, "--check")
        assert (tree / "src/ItemVersion/Locales/deDE.lua").read_text(
            encoding="utf-8"
        ) == before

    def test_fix_mode_writes_stubs(self, tree):
        assert self.run(tree) == 0
        text = (tree / "src/ItemVersion/Locales/deDE.lua").read_text(encoding="utf-8")
        assert '-- L["Beta"] = ""' in text

    def test_fix_mode_reports_the_state_it_leaves_behind(self, tree, capsys):
        """A run that fixes everything must not still print what it fixed."""
        (tree / "src/ItemVersion/Locales/deDE.lua").write_text(
            DEUTSCH_HEADER + 'L["Beta"] = "B"\nL["Alpha"] = "A"\n', encoding="utf-8"
        )
        assert self.run(tree) == 0
        assert "0 error(s), 0 warning(s)" in capsys.readouterr().out

    def test_check_mode_still_reports_what_it_found(self, tree, capsys):
        """The mirror of the above: --check fixes nothing, so it must complain."""
        (tree / "src/ItemVersion/Locales/deDE.lua").write_text(
            DEUTSCH_HEADER + 'L["Beta"] = "B"\nL["Alpha"] = "A"\n', encoding="utf-8"
        )
        assert self.run(tree, "--check") == 0
        assert "not sorted" in capsys.readouterr().out

    def test_fix_mode_never_rewrites_enUS(self, tree):
        """enUS is hand-written and carries comments explaining its keys."""
        path = tree / "src/ItemVersion/Locales/enUS.lua"
        annotated = (
            'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\n'
            "-- a comment a maintainer wrote and expects to keep\n"
            'L["Alpha"] = true\n'
            'L["Beta"] = true\n'
        )
        path.write_text(annotated, encoding="utf-8")

        assert self.run(tree) == 0
        assert path.read_text(encoding="utf-8") == annotated

    def test_missing_enUS_is_a_hard_failure(self, tree):
        """With no default there is nothing to check against, so do not guess."""
        (tree / "src/ItemVersion/Locales/enUS.lua").unlink()
        assert self.run(tree) == 1

    def test_used_but_undefined_fails(self, tree, capsys):
        (tree / "src/ItemVersion/Thing.lua").write_text(
            'print(L["Ghost"])\n', encoding="utf-8"
        )
        assert self.run(tree, "--check") == 1
        assert "enUS does not define it" in capsys.readouterr().out

    def test_bad_placeholder_fails(self, tree, capsys):
        (tree / "src/ItemVersion/Locales/enUS.lua").write_text(
            'local L = LibStub("AceLocale-3.0"):NewLocale(A, "enUS", true)\n'
            'L["Hit %d times"] = true\n',
            encoding="utf-8",
        )
        (tree / "src/ItemVersion/Thing.lua").write_text(
            'print(L["Hit %d times"])\n', encoding="utf-8"
        )
        (tree / "src/ItemVersion/Locales/deDE.lua").write_text(
            DEUTSCH_HEADER + 'L["Hit %d times"] = "%s mal getroffen"\n',
            encoding="utf-8",
        )
        assert self.run(tree, "--check") == 1
        assert "placeholder mismatch" in capsys.readouterr().out

    def test_check_mode_fails_without_fixing(self, tree):
        """CI must not paper over a problem by rewriting the file."""
        (tree / "src/ItemVersion/Locales/deDE.lua").write_text(
            DEUTSCH_HEADER + 'L["Nonsense"] = "X"\n', encoding="utf-8"
        )
        assert self.run(tree, "--check") == 1
        assert "Nonsense" in (tree / "src/ItemVersion/Locales/deDE.lua").read_text(
            encoding="utf-8"
        )
