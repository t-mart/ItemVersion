local _, Private = ...

local ItemVersion = ItemVersion

function ItemVersion.getVersion(itemId)
  -- caller must ensure that itemId is a number

  local versionId = Private.itemIdToVersionId[itemId]

  -- item id not found in database
  if not versionId then
    return nil
  end

  return Private.versionIdToVersion[versionId]
end

function ItemVersion.getVersionExpac(version)
  return Private.majorToExpac[version.major]
end
