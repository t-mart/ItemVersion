local _, Private = ...

-- Development-only, in-client test suite. This file never ships: wowaddon.yml lists
-- it under `dev-only`, so `./dev build` drops the file and strips this line from the
-- packaged TOC. It only loads in a symlinked dev install. Run it in game with
-- /ivtest.
--
-- This is Layer 2 of the test plan (see TODO.md). It covers only what the busted
-- suite in tests/ cannot reach: the addon's interfacing with the live client, above
-- all the tooltip hook. Pure logic (the lookup, corrections, token formatting) is
-- tested out of client and does not belong here.

local AceConsole = LibStub("AceConsole-3.0")
local Color = Private.Color

local PASS = { r = 0.2, g = 0.8, b = 0.2 }
local FAIL = { r = 0.9, g = 0.2, b = 0.2 }
local SKIP = { r = 0.9, g = 0.8, b = 0.2 }

local function tag(color, label)
  return Color.WrapTextWithColor(label, color)
end

-- Collects results and prints a summary once every check has reported. Some checks
-- finish asynchronously, so the suite counts how many it expects and prints the
-- summary when the last one lands.
local function newReport(expected)
  local report = { pass = 0, fail = 0, skip = 0, seen = 0, expected = expected }

  local function record(bucket)
    report[bucket] = report[bucket] + 1
    report.seen = report.seen + 1
    if report.seen == report.expected then
      AceConsole:Print(
        string.format(
          "ItemVersion in-client tests: %d passed, %d failed, %d skipped",
          report.pass,
          report.fail,
          report.skip
        )
      )
    end
  end

  function report:ok(name)
    AceConsole:Print(string.format("%s %s", tag(PASS, "[PASS]"), name))
    record("pass")
  end

  function report:no(name, why)
    AceConsole:Print(string.format("%s %s -- %s", tag(FAIL, "[FAIL]"), name, why or ""))
    record("fail")
  end

  function report:meh(name, why)
    AceConsole:Print(string.format("%s %s -- %s", tag(SKIP, "[SKIP]"), name, why or ""))
    record("skip")
  end

  return report
end

-- The first item id the database resolves, reconstructed the way API.lua does. Gives
-- the client-side checks a real, present item to work with.
local function knownItemId()
  local pos = 0
  for i = 1, #Private.runStartDeltas do
    local start = pos + Private.runStartDeltas[i]
    if Private.API.GetItemVersion(start, false) then
      return start
    end
    pos = start + Private.runLengths[i]
  end
  return nil
end

-- Confirms the data file actually loaded in the client and a lookup returns the
-- shape the tooltip path depends on.
local function checkDatabaseLoaded(report)
  local id = knownItemId()
  if not id then
    report:no("database loaded", "no item id resolved from the data")
    return
  end

  local lookup = Private.API.GetItemVersion(id, false)
  if lookup and lookup.expansion and lookup.expansion.canonName then
    report:ok(string.format("database loaded (item %d in %s)", id, lookup.expansion.canonName))
  else
    report:no("database loaded", "lookup returned an unexpected shape")
  end
end

-- The addon hooks tooltips one of two ways depending on the flavor. If neither path
-- exists, HookTooltip would have errored on load, so assert one is available.
local function checkTooltipHookPath(report)
  local classic = GameTooltip:HasScript("OnTooltipSetItem") and ItemRefTooltip:HasScript("OnTooltipSetItem")
  if classic then
    report:ok("tooltip hook path available (OnTooltipSetItem)")
  elseif TooltipDataProcessor then
    report:ok("tooltip hook path available (TooltipDataProcessor)")
  else
    report:no("tooltip hook path available", "neither OnTooltipSetItem nor TooltipDataProcessor")
  end
end

-- The modifier gating upvalues these at load; a flavor missing one would break the
-- gate. Meta is Mac-only, so it is not required.
local function checkModifierGlobals(report)
  local missing = {}
  for _, name in ipairs({ "IsShiftKeyDown", "IsControlKeyDown", "IsAltKeyDown" }) do
    if type(_G[name]) ~= "function" then
      table.insert(missing, name)
    end
  end
  if #missing == 0 then
    report:ok("modifier key globals present")
  else
    report:no("modifier key globals present", "missing " .. table.concat(missing, ", "))
  end
end

-- The flagship client check: drive a real item tooltip and confirm our hook injects
-- the version line. Item data can load asynchronously, so it retries briefly and
-- skips rather than fails if the client never serves the item.
local function checkTooltipInjection(report)
  local id = knownItemId()
  if not id then
    report:meh("tooltip injects the version line", "no known item id")
    return
  end

  local profile = Private.Database.profile

  -- Force a state where the line must show: tooltip on, no modifier gate. Saved and
  -- restored so a dev's own settings survive the run.
  local saved = {
    enableTooltip = profile.enableTooltip,
    showOnShift = profile.showOnShift,
    showOnControl = profile.showOnControl,
    showOnAlt = profile.showOnAlt,
    showOnMeta = profile.showOnMeta,
  }
  local function restore()
    for key, value in pairs(saved) do
      profile[key] = value
    end
  end

  profile.enableTooltip = true
  profile.showOnShift = false
  profile.showOnControl = false
  profile.showOnAlt = false
  profile.showOnMeta = false

  local lookup = Private.API.GetItemVersion(id, profile.applyCorrections)
  local needle = lookup:Format(profile.tooltipFormat)

  local attempts = 0
  local function attempt()
    attempts = attempts + 1

    GameTooltip:SetOwner(UIParent, "ANCHOR_NONE")
    GameTooltip:ClearLines()
    local ok = pcall(GameTooltip.SetItemByID, GameTooltip, id)
    if not ok then
      GameTooltip:Hide()
      restore()
      report:meh("tooltip injects the version line", "SetItemByID unavailable on this flavor")
      return
    end

    for i = 1, GameTooltip:NumLines() do
      local fontString = _G["GameTooltipTextLeft" .. i]
      local text = fontString and fontString:GetText()
      if text and text:find(needle, 1, true) then
        GameTooltip:Hide()
        restore()
        report:ok(string.format("tooltip injects the version line (item %d)", id))
        return
      end
    end

    GameTooltip:Hide()

    if attempts < 5 then
      C_Timer.After(0.3, attempt)
    else
      restore()
      report:meh(
        "tooltip injects the version line",
        "no matching line after loading item " .. id .. " (item data may be uncached)"
      )
    end
  end

  attempt()
end

local CHECKS = {
  checkDatabaseLoaded,
  checkTooltipHookPath,
  checkModifierGlobals,
  checkTooltipInjection,
}

local function run()
  AceConsole:Print("Running ItemVersion in-client tests...")
  local report = newReport(#CHECKS)
  for _, check in ipairs(CHECKS) do
    check(report)
  end
end

AceConsole:RegisterChatCommand("ivtest", run)
