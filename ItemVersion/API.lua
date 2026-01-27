local AddonName, Private = ...

local Expansion = Private.Expansion

Private.API = {}

---Get the version for a given item, or nil if it does not exist in the database
---@param itemId number
---@param applyVersionCorrections boolean | nil
---@return { expansion: table, minor: number, patch: number, build: number, isCorrected: boolean} | nil
function Private.API.GetItemVersion(itemId, applyVersionCorrections)
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

function Private.API.FormatTooltipString(formatString, lookup)
  local expacLong = lookup.expansion.canonName
  local expacShort = lookup.expansion.shortName

  -- can we do this better?
  local expansion = Expansion:GetExpansionFromMajor(lookup.expansion.major)
  local expacIcon = format("|T%s:16:32|t", expansion.texture)

  local versionTriple = format("%d.%d.%d", lookup.expansion.major, lookup.minor, lookup.patch)
  local versionFull = format("%d.%d.%d.%d", lookup.expansion.major, lookup.minor, lookup.patch, lookup.build)
  local buildNumber = tostring(lookup.build)

  return formatString
      :gsub("{expacShort}", expacShort)
      :gsub("{expacLong}", expacLong)
      :gsub("{expacIcon}", expacIcon)
      :gsub("{versionFull}", versionFull)
      :gsub("{versionTriple}", versionTriple)
      :gsub("{buildNumber}", buildNumber)
end
