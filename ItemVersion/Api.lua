local AddonName, Private = ...

function ItemVersion.getItemVersion(itemId)
    return Private.versionIdToVersion[Private.itemIdToVersionId[itemId]]
end

function ItemVersion.getItemExpac(itemId)
    return
        Private.majorToExpac[
          Private.versionIdToVersion[
            Private.itemIdToVersionId[itemId]
          ].major
        ]
end

function ItemVersion.versionString(version)
  return format("%d.%d.%d.%d", version.major, version.minor, version.patch, version.build)
end
