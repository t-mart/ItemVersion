local _, AddonTable = ...

---Get the version for a given item, or nil if it does not exist in the database
---@param itemId number
---@return {major: number, minor: number, patch: number, build: number } | nil
function AddonTable.getItemVersion(itemId)
  -- caller must ensure that itemId is a number
  local versionId = AddonTable.itemIdToVersionId[itemId]

  -- item id not found in database
  if versionId == nil then
    return nil
  end

  return AddonTable.versionIdToVersion[versionId]
end

---Get the expansion for a given version (from it's major field), or nil if it does not exist in the
---database.
---@param version { major: number }
---@return {canonName:string,shortName:string}|nil asdf
function AddonTable.getVersionExpac(version)
  return AddonTable.majorToExpac[version.major]
end

---Return a dot-separated string of the components of version
---@param version {major: number, minor: number, patch: number, build: number }
---@return string
function AddonTable.buildVersionString(version)
  return format("%d.%d.%d.%d", version.major, version.minor, version.patch,
                version.build)
end

-- expose API functions
ItemVersion.getItemVersion = AddonTable.getItemVersion
ItemVersion.getVersionExpac = AddonTable.getVersionExpac
ItemVersion.buildVersionString = AddonTable.buildVersionString
