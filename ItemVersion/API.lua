local _, Private = ...

local Expansion = Private.Expansion
local Table = Private.Table

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

---Format a string by replacing tokens with values from the lookup
---@param formatString string The format string containing tokens like {expacLong}, {versionTriple}, etc.
---@return string formatted The formatted string with tokens replaced
function ItemLookupMixin:Format(formatString)
  for _, tokenInfo in ipairs(Private.Tokens) do
    local resolved = tokenInfo.resolve(self)
    formatString = formatString:gsub(tokenInfo.string, resolved)
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
      return Table.Mixin({
        expansion = toLookupExpansion(expansion),
        minor = 0,
        patch = 0,
        build = 0,
        isCorrected = true,
      }, ItemLookupMixin)
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

  return Table.Mixin({
    expansion = toLookupExpansion(expansion),
    minor = version.minor,
    patch = version.patch,
    build = version.build,
    isCorrected = false,
  }, ItemLookupMixin)
end
