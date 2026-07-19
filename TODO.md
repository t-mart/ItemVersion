# ItemVersion TODO

## Lua test suite

Goal: exercise the addon's Lua directly, since the shipping interface is the WoW
client (manual, no ecosystem libraries). Two layers, because they cover different
things. Layer 1 is the priority; Layer 2 is thin and esoteric.

The addon is well factored for this: the correctness-critical logic in API.lua
(version lookup, binary search, run reconstruction, corrections, token
replacement), Tokens.lua, Expansion.lua, Color.lua, and Table.lua is essentially
pure Lua. Its only non-stdlib touch points are the `local _, Private = ...` addon
vararg, the global `format`, and `LibStub` (used to fetch the AceLocale `L`). So
the mocking surface for the core is tiny. Only Tooltip.lua, Options.lua, and the
AceDB part of Profile.lua genuinely need the client.

### Layer 1: out-of-WoW unit suite (priority) -- DONE

Landed. Harness in `tests/helper.lua`, specs in `tests/`, run by `./dev test`.
41 assertions, ~0.3s. Kept for reference below is the plan it was built to.

- Framework: busted. Installable on Arch (luarocks) and on GHA runners, so CI can
  run it.
- Interpreter target: PUC-Rio Lua 5.1, the version WoW actually ships (a
  customized 5.1.x, not LuaJIT). Run busted under 5.1 so 5.1-only pitfalls surface
  (no `//` integer divide, `#` behavior, number-to-string formatting). This is the
  class of bug that a past data-format change hit with `//`.
- Location: `tests/` at the repo root (conventional, and keeps it distinct from
  the Python `tooling/tests/`).
- Harness: a small bootstrap that
  - creates a shared `Private` table,
  - stubs the globals the core needs: `format = string.format` and a `LibStub`
    that returns a fake AceLocale whose `L[key]` yields the key back,
  - loads each core file in TOC order via `loadfile(path)("ItemVersion", Private)`
    (Table, Color, Expansion, Tokens, ItemData, API), skipping the client-only
    files,
  - hands the specs `Private.API` and friends to assert against.
- Coverage to write:
  - `API.GetItemVersion` boundaries: first id, last id, run edges, ids in gaps
    (absent), empty-run degenerate case.
  - Corrections precedence: a corrected item resolves to its correction, not the
    main-database row; `applyVersionCorrections` false skips corrections.
  - `replacePlain` / `Format` literal-replacement edge cases the code calls out in
    API.lua: values containing `%` (from translated names) and tokens/values
    containing `-`; empty-needle guard.
  - Token resolution for every entry in Tokens.lua against a known lookup.
  - Expansion major -> expansion mapping (`GetExpansionFromMajor`,
    `GetCorrectedExpansionForItemId`).
  - Property test: `findVersion` vs a brute-force expansion of the runs across the
    whole real ItemData.lua, asserting 0 mismatches. (This was run once ad hoc
    during the RLE change and thrown away; make it permanent.)

### Layer 2: in-client suite (thin, manual, must not ship) -- DONE

Landed as `src/ItemVersion/DevTests.lua`, run in game with `/ivtest`. Listed under
`dev-only` in wowaddon.yml so the build drops it and strips its TOC line; loads only
in a symlinked dev install. Checks: database loaded, tooltip hook path available,
modifier globals present, and the flagship tooltip-injection check (drives a real
GameTooltip, retries for async item loads, skips if uncached). Still unverified in a
live client on my side -- needs a play test. The plan it was built to is kept below.

- A dev-only Lua file that registers a slash command (e.g. `/iv test`) and asserts
  only against things the mock cannot reach: that the tooltip hook actually injects
  a line into a real `GameTooltip`, that `TooltipDataProcessor` wiring fires, and
  that the keybind modifier gating works. Prints pass/fail to chat.
- Keep it small. Anything a Layer 1 mock can cover does not belong here.
- It must not ship in the packaged build. Mechanics below.

#### Not shipping the in-client file

WoW loads addon files listed in the TOC (Bindings.xml is special-cased and
auto-loads without a TOC entry, which is why it is only in `wowaddon.yml`'s
`ignore` today; an arbitrary test file gets no such treatment and needs a TOC
line to load in dev).

Plan: reuse the build's existing TOC rewrite. `cmd_build` already copies the
source through `shutil.ignore_patterns(*ignore)` and rewrites the staged TOC
(stamp_build_date). So:

- Keep the test file present in `src/ItemVersion/` and referenced in the TOC, so a
  symlinked dev install loads it.
- Add a `dev-only:` list to `wowaddon.yml` (distinct from `ignore`, which is
  ignore-but-not-in-TOC like Bindings.xml). At build time: exclude those files from
  the copy AND strip their referencing lines from the staged TOC. The shipped zip
  then has neither the file nor the TOC reference.
- Alternative if we want zero new config: strip any staged-TOC line whose target
  file is absent from the staged tree (i.e. was ignored), and just add the test
  file to `ignore`. Cleaner config, but overloads `ignore`'s meaning. Leaning
  toward the explicit `dev-only:` key for clarity.

### dev tooling changes

- DONE `./dev test` runs the Layer 1 busted suite (the short name, since it is what
  most contributors reach for). Locates busted on PATH or in a Lua 5.1 rock tree.
- DONE `./dev test-tooling` runs the Python tooling suite (the former `cmd_test`
  pytest run, renamed).
- DONE `./dev check` runs the Lua suite alongside lint/format/locales, and
  `./dev watch` inherits it (it re-runs check on save).
- DONE docs updated (CONTRIBUTING.md gained a Running the Tests section; the
  prerequisites list mentions busted).
- DONE build-side: `wowaddon.yml`'s `ignore` was renamed to `dev-only` (one concept:
  Bindings.xml and DevTests.lua both live there). `cmd_build` drops those files and
  `toc.strip_files` removes any TOC line referencing them, so the in-client file
  never ships. Covered by test_toc.py and test_packaging.py.

### CI changes

- DONE the checks workflow installs Lua 5.1 + luarocks + busted and runs
  `./dev check` (which now includes the Lua suite).
- DONE the workflow also runs `./dev test-tooling` as its own step (the pytest
  suite that never used to run in CI).

### Prerequisites (installed)

- Arch dev env: `lua51`, `luarocks`, busted (via `luarocks --lua-version 5.1
  --local install busted`, or the `lua51-busted` package).
- CI: `leafo/gh-actions-lua` (5.1) + `leafo/gh-actions-luarocks` + `luarocks
  install busted`, pinned.

### Open questions

- RESOLVED: one `dev-only` key, not two. Bindings.xml and DevTests.lua are the same
  kind of thing (dev-only, never shipped); they differ only in load mechanism.
- RESOLVED: `./dev check` runs the Lua suite (and so does watch).

### Linting the tests -- DONE

- `tests/` is now formatted by stylua (shares stylua.toml) and linted by selene
  against its own std, `tests/busted.yml` (Lua 5.1 base plus busted/luassert
  globals, `global_usage` allowed for the harness's `_G` stubbing). `./dev check`
  runs selene twice (addon with wow-stdlib, tests with the busted std) and stylua
  over both trees; `./dev format` formats both; `./dev watch` also watches `tests/`.

## Next up

- Play-test `/ivtest` in a live client (retail + a classic flavor) and adjust the
  tooltip-injection check against real behavior. (Confirmed green once by hand.)
