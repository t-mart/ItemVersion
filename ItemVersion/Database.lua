local _, ItemVersion = ...

local AceDB = LibStub("AceDB-3.0")

ItemVersion.Database = {}

function ItemVersion.Database:GetDefault()
  return {
    profile = {
      showPrefix = true,
      prefixColor = { r = 1.0, g = 1.0, b = 1.0 },
      shortExpacNames = false,
      expacColor = { r = 1.0, g = 1.0, b = 1.0 },
      showVersion = true,
      versionColor = { r = 1.0, g = 1.0, b = 1.0 },
      showWhenMissing = false,
      keyModifiers = { shift = false, control = false, alt = false, meta = false },
      includeCommunityUpdates = true,
    },
  }
end

function ItemVersion.Database:New()
  return AceDB:New("ItemVersionDB", self:GetDefault(), true)
end
