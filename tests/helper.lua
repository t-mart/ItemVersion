-- Loads ItemVersion's pure-logic files outside the WoW client.
--
-- Each addon file is a chunk that WoW calls with (AddonName, Private). We stub the
-- handful of globals the core touches, then load the files in TOC order into a
-- shared Private table. The client-only files (Init, Profile, Options,
-- SlashCommands, Tooltip) are intentionally left out; they need the real client.

local M = {}

local ADDON_NAME = "ItemVersion"

-- Relative to the repo root, which is where the ./dev tooling runs busted from.
local SRC = "src/ItemVersion"

-- TOC order, minus the client-only files. ItemData must precede API, which reads
-- the run arrays it defines; Table precedes Expansion, which mixes in with it.
local FILES = { "Table", "Color", "Expansion", "Tokens", "ItemData", "API" }

-- Stand-in for the AceLocale table. With no translation registered, AceLocale hands
-- back the key itself, so L[k] == k here. Translations are not what this suite
-- exercises, and this keeps expansion names deterministic without a generated
-- locale file on disk.
local function makeLocale()
  return setmetatable({}, {
    __index = function(_, key)
      return key
    end,
  })
end

-- Only the libraries the core actually asks for. Anything else is a bug in the
-- harness's assumptions, so fail loudly rather than return nil.
local function makeLibStub(locale)
  local libs = {
    ["AceLocale-3.0"] = {
      GetLocale = function()
        return locale
      end,
    },
  }
  return function(name)
    local lib = libs[name]
    assert(lib, "harness LibStub has no stub for " .. tostring(name))
    return lib
  end
end

local cached

-- Load the addon once and hand back its Private table. The suite is read-only, so a
-- single shared load is safe and keeps the big ItemData parse off every spec.
function M.load()
  if cached then
    return cached
  end

  local Private = {}

  _G.format = string.format
  _G.LibStub = makeLibStub(makeLocale())
  -- Call-time only, in Expansion:IsPresent. A value past the last major keeps every
  -- expansion "present" for anything that reaches for it.
  _G.GetClientDisplayExpansionLevel = function()
    return 99
  end

  for _, name in ipairs(FILES) do
    local chunk = assert(loadfile(SRC .. "/" .. name .. ".lua"))
    chunk(ADDON_NAME, Private)
  end

  cached = Private
  return cached
end

-- Reconstruct the absolute run table from the deltas, the same way API.lua does on
-- load. Ground truth for the lookup specs: a plain list they can scan linearly and
-- compare against the addon's binary search.
function M.reconstructRuns(Private)
  local runs = {}
  local pos = 0
  for i = 1, #Private.runStartDeltas do
    local start = pos + Private.runStartDeltas[i]
    runs[i] = {
      start = start,
      length = Private.runLengths[i],
      versionId = Private.runVersions[i],
    }
    pos = start + Private.runLengths[i]
  end
  return runs
end

-- The set of major versions that map to a known expansion. findVersion can locate a
-- run whose major has no expansion, in which case GetItemVersion returns nil.
function M.knownMajors(Private)
  local majors = {}
  for _, expansion in ipairs(Private.Expansion.All) do
    majors[expansion.major] = true
  end
  return majors
end

return M
