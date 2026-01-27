local _, Private = ...

local Expansion = Private.Expansion

Private.API = {}
local API = Private.API

---@class ItemVersionLookup
---@field expansion {major: number, canonName: string, shortName: string}
---@field minor number
---@field patch number
---@field build number
---@field isCorrected boolean

---Get the version for a given item, or nil if it does not exist in the database
---@param itemId number The item ID to look up
---@param applyVersionCorrections boolean|nil Whether to apply version corrections
---@return ItemVersionLookup|nil lookup The version information, or nil if not found
function API.GetItemVersion(itemId, applyVersionCorrections)
  -- first lookup in corrections
  local expansion
  if applyVersionCorrections then
    expansion = Expansion:GetCorrectedExpansionForItemId(itemId)
    if expansion then
      return {
        expansion = {
          major = expansion.major,
          canonName = expansion.canonName,
          shortName = expansion.shortName,
        },
        minor = 0,
        patch = 0,
        build = 0,
        isCorrected = true,
      }
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

  return {
    expansion = {
      major = expansion.major,
      canonName = expansion.canonName,
      shortName = expansion.shortName,
    },
    minor = version.minor,
    patch = version.patch,
    build = version.build,
    isCorrected = false,
  }
end

---Format a tooltip string by replacing tokens with values from the lookup
---@param formatString string The format string containing tokens like {expacLong}, {versionTriple}, etc.
---@param lookup ItemVersionLookup The version lookup data
---@return string formatted The formatted string with tokens replaced
function API.FormatTooltip(formatString, lookup)
  for _, tokenInfo in ipairs(Private.Tokens) do
    local resolved = tokenInfo.resolve(lookup)
    formatString = formatString:gsub(tokenInfo.string, resolved)
  end

  return formatString
end
