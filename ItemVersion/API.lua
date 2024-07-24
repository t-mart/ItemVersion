local _, ItemVersion = ...

local Expac = ItemVersion.Expac

ItemVersion.API = {}

---Get the version for a given item, or nil if it does not exist in the database
---@param itemId number
---@param includeCommunityUpdates boolean | nil
---@return {major: number, minor: number, patch: number, build: number } | nil
function ItemVersion.API:getItemVersion(itemId, includeCommunityUpdates)
  local itemIdToVersionId, versionIdToVersion

  if includeCommunityUpdates then
    itemIdToVersionId = ItemVersion.communityItemIdToVersionId
    versionIdToVersion = ItemVersion.communityVersionIdToVersion
  else
    itemIdToVersionId = ItemVersion.itemIdToVersionId
    versionIdToVersion = ItemVersion.versionIdToVersion
  end

  local versionId = itemIdToVersionId[itemId]

  -- item id not found in database
  if versionId == nil then
    return nil
  end

  return versionIdToVersion[versionId]
end

---Get the expansion for a given version (from it's major field), or nil if it does not exist in the
---database.
---@param version { major: number }
---@return {canonName:string,shortName:string} | nil
function ItemVersion.API:getVersionExpac(version)
  return Expac:GetExpacFromMajor(version.major)
end

---Return a dot-separated string of the components of version
---@param version {major: number, minor: number, patch: number, build: number }
---@param includeBuildNumber boolean if true, include the build number in the string
---@return string
function ItemVersion.API:buildVersionString(version, includeBuildNumber)
  if includeBuildNumber then
    return string.format("%d.%d.%d.%d", version.major, version.minor, version.patch, version.build)
  else
    return string.format("%d.%d.%d", version.major, version.minor, version.patch)
  end
end
