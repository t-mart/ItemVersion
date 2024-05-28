-- Some items were added to the game in a version/expansion earlier than the one in which they were
-- usable by players. For example, the herb Marrowroot was added during the end of BfA, but only
-- usable in SL. In this case, BfA would be "canonical" version/expansion.
--
-- Here, we attempt to "correct" this problem by providing the expansion that players probably
-- expect to see. From the above example, with this update, we should show SL as the expansion for
-- Marrowroot.

local addonName, ItemVersion = ...

local L = LibStub("AceLocale-3.0"):GetLocale(addonName)
local Expac = ItemVersion.Expac

-- When an item's added-in expansion is different than its usable-in expansion, add it here to the
-- appropriate list.
-- for example, Marrowroot (168589) should go in the Shadowlands list.
-- Please follow the format and keep the lists numerically sorted
local communityUpdates = {
  [L["Classic"]] = {},
  [L["The Burning Crusade"]] = {},
  [L["Wrath of the Lich King"]] = {},
  [L["Cataclysm"]] = {},
  [L["Mists of Pandaria"]] = {},
  [L["Warlords of Draenor"]] = {},
  [L["Legion"]] = {},
  [L["Battle for Azeroth"]] = {},
  [L["Shadowlands"]] = {
    168583, -- Widowbloom
    168586, -- Rising Glory
    168589, -- Marrowroot
    169701, -- Death Blossom
    171315, -- Nightshade
  },
  [L["Dragonflight"]] = {},
  [L["The War Within"]] = {},
}

-- cause tbl to use backupTbl for key lookups if key is not in tbl
-- the original metatable is used if it exists. otherwise, a new one
-- is created. in both cases, the __index function is overwritten
local function SetBackupTable(tbl, backupTbl)
  local getitem = function(_, key)
    return backupTbl[key]
  end

  local curMT = getmetatable(tbl)
  if curMT then
    curMT.__index = getitem
  else
    setmetatable(tbl, { __index = getitem })
  end
end

-- put the communityUpdates table into the same form as Data.lua's itemIdToVersionId
ItemVersion.communityItemIdToVersionId = {}
for canonName, itemIds in pairs(communityUpdates) do
  local versionId = -Expac:GetExpacIdFromCanonName(canonName) -- negate
  for _, itemId in ipairs(itemIds) do
    ItemVersion.communityItemIdToVersionId[itemId] = versionId
  end
end
SetBackupTable(ItemVersion.communityItemIdToVersionId, ItemVersion.itemIdToVersionId)

-- placeholder versions for community updates
-- these don't truly exist, but will have the expected major version number (so the expac will look
-- right)
ItemVersion.communityVersionIdToVersion = {
  -- use negative numbers that won't collide with canonical version ids
  [-1] = { major = 1, minor = 0, patch = 0, build = 0 }, -- classic
  [-2] = { major = 2, minor = 0, patch = 0, build = 0 }, -- tbc
  [-3] = { major = 3, minor = 0, patch = 0, build = 0 }, -- wotlk
  [-4] = { major = 4, minor = 0, patch = 0, build = 0 }, -- cata
  [-5] = { major = 5, minor = 0, patch = 0, build = 0 }, -- mop
  [-6] = { major = 6, minor = 0, patch = 0, build = 0 }, -- wod
  [-7] = { major = 7, minor = 0, patch = 0, build = 0 }, -- legion
  [-8] = { major = 8, minor = 0, patch = 0, build = 0 }, -- bfa
  [-9] = { major = 9, minor = 0, patch = 0, build = 0 }, -- sl
  [-10] = { major = 10, minor = 0, patch = 0, build = 0 }, -- df
  [-11] = { major = 11, minor = 0, patch = 0, build = 0 }, -- ww
}
SetBackupTable(ItemVersion.communityVersionIdToVersion, ItemVersion.versionIdToVersion)
