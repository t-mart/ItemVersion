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
  local versionId = Private.itemIdToVersionId[itemId]
  if not versionId then
    return nil
  end

  local version = Private.versionIdToVersion[versionId]
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
