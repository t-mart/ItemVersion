local addonName, addonTable = ...

ItemVersion = LibStub("AceAddon-3.0"):GetAddon(addonName)

---Get the version for a given item, or nil if it does not exist in the database
---@param itemId number
---@return {major: number, minor: number, patch: number, build: number } | nil
function ItemVersion:getItemVersion(itemId)
  -- caller must ensure that itemId is a number
  local versionId = addonTable.itemIdToVersionId[itemId]

  -- item id not found in database
  if versionId == nil then
    return nil
  end

  return addonTable.versionIdToVersion[versionId]
end

---Get the expansion for a given version (from it's major field), or nil if it does not exist in the
---database.
---@param version { major: number }
---@return {canonName:string,shortName:string} | nil
function ItemVersion:getVersionExpac(version)
  return self:getExpacFromMajor(version.major)
end

---Return a dot-separated string of the components of version
---@param version {major: number, minor: number, patch: number, build: number }
---@return string
function ItemVersion:buildVersionString(version)
  return string.format("%d.%d.%d.%d", version.major, version.minor, version.patch,
                       version.build)
end
