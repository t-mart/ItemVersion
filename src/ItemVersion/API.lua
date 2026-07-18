local _, Private = ...

local Expansion = Private.Expansion

Private.API = {}
local API = Private.API

--Turn an Expansion into one that goes into the lookup
--@param expansion Expansion The expansion to convert
--@return table The lookup expansion data
local function toLookupExpansion(expansion)
  return {
    major = expansion.major,
    canonName = expansion.canonName,
    shortName = expansion.shortName,
  }
end

-- Absolute run starts, reconstructed once from the deltas in ItemData.lua. Item ids
-- sorted ascending are covered by contiguous runs that each share one version;
-- an id no run covers was absent from the source. ItemData.lua loads before this
-- file (see the TOC), so the run arrays are already present.
local runStarts = {}
do
  local pos = 0
  for i = 1, #Private.runStartDeltas do
    local start = pos + Private.runStartDeltas[i]
    runStarts[i] = start
    pos = start + Private.runLengths[i]
  end
end

---Find the version that covers an item id, or nil if no run covers it
---@param itemId number The item ID to look up
---@return {major: number, minor: number, patch: number, build: number}|nil
local function findVersion(itemId)
  local count = #runStarts
  if count == 0 then
    return nil
  end

  -- Binary search for the greatest runStarts[i] <= itemId.
  local lo, hi = 1, count
  while lo < hi do
    local mid = math.floor((lo + hi + 1) / 2)
    if runStarts[mid] <= itemId then
      lo = mid
    else
      hi = mid - 1
    end
  end

  -- The item is present only if it falls within that run's covered ids.
  local start = runStarts[lo]
  if itemId < start or itemId > start + Private.runLengths[lo] - 1 then
    return nil
  end

  -- runVersions is 0-based; versionIdToVersion is 1-indexed, so version id v
  -- lives at index v + 1. Each row is {major, minor, patch, build}.
  local row = Private.versionIdToVersion[Private.runVersions[lo] + 1]
  if not row then
    return nil
  end

  return { major = row[1], minor = row[2], patch = row[3], build = row[4] }
end

local ItemLookupMixin = {}

-- Shared by every lookup rather than copied into each one. The mixin is fixed,
-- so there is nothing per-lookup to copy, and this keeps Format off the result
-- itself, where it would otherwise turn up in pairs() alongside the data.
local ItemLookupMeta = { __index = ItemLookupMixin }

---Replaces every occurrence of needle in subject, matching literally
---
---Deliberately not gsub, which reads the needle as a pattern and the replacement
---as a replacement string. Both sides carry text that can contain the characters
---those grammars reserve: a token could one day hold a `-`, and a resolved value
---can hold a `%`, since expansion names come from translators.
---@param subject string The string to search
---@param needle string The literal text to find
---@param replacement string The literal text to put in its place
---@return string
local function replacePlain(subject, needle, replacement)
  -- An empty needle matches at every position without advancing, so the loop
  -- below would never terminate. No token is empty, but a hung client is a
  -- steep price for being wrong about that.
  if needle == "" then
    return subject
  end

  local pieces = {}
  local searchFrom = 1

  while true do
    local matchStart, matchEnd = subject:find(needle, searchFrom, true)
    if not matchStart then
      break
    end

    table.insert(pieces, subject:sub(searchFrom, matchStart - 1))
    table.insert(pieces, replacement)
    searchFrom = matchEnd + 1
  end

  table.insert(pieces, subject:sub(searchFrom))

  return table.concat(pieces)
end

---Format a string by replacing tokens with values from the lookup
---@param formatString string The format string containing tokens like {expacLong}, {versionTriple}, etc.
---@return string formatted The formatted string with tokens replaced
function ItemLookupMixin:Format(formatString)
  for _, tokenInfo in ipairs(Private.Tokens) do
    formatString = replacePlain(formatString, tokenInfo.string, tokenInfo.resolve(self))
  end

  return formatString
end

---@class ItemVersionLookup
---@field expansion {major: number, canonName: string, shortName: string}
---@field minor number
---@field patch number
---@field build number
---@field isCorrected boolean

---Get the version for a given item, or nil if it does not exist in the database
---@param itemId number The item ID to look up
---@param applyVersionCorrections boolean|nil Whether to apply version corrections that fix items whose release version is different than their usable version.
---@return ItemVersionLookup|nil lookup The version information, or nil if not found
function API.GetItemVersion(itemId, applyVersionCorrections)
  -- first lookup in corrections
  local expansion
  if applyVersionCorrections then
    expansion = Expansion:GetCorrectedExpansionForItemId(itemId)
    if expansion then
      return setmetatable({
        expansion = toLookupExpansion(expansion),
        minor = 0,
        patch = 0,
        build = 0,
        isCorrected = true,
      }, ItemLookupMeta)
    end
  end

  -- then lookup in main database
  local version = findVersion(itemId)
  if not version then
    return nil
  end

  expansion = Expansion:GetExpansionFromMajor(version.major)
  if not expansion then
    return nil
  end

  return setmetatable({
    expansion = toLookupExpansion(expansion),
    minor = version.minor,
    patch = version.patch,
    build = version.build,
    isCorrected = false,
  }, ItemLookupMeta)
end
