local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)

---@class Expansion
---@field major number The major version number (e.g., 1 for Classic, 2 for TBC)
---@field canonName string The full canonical name of the expansion
---@field shortName string The abbreviated name of the expansion
---@field previewItemId number Item ID used for preview icon
---@field texture string Path to the expansion icon texture
---@field expansionLevel number The expansion level as returned by GetClientDisplayExpansionLevel()
---@field corrections number[]|nil Optional list of item IDs that need version correction
---@field IsPresent fun(self: Expansion): boolean Check if this expansion is available

Private.Expansion = {}

---Returns the texture path for an expansion icon
---@param fileName string The filename of the expansion icon
---@return string path The full texture path
local function getExpansionTexturePath(fileName)
  return "Interface\\AddOns\\" .. AddonName .. "\\Media\\Images\\Expansions\\" .. fileName
end

Private.Expansion.All = {
  {
    major = 1,
    canonName = L["World of Warcraft"],
    shortName = L["Vanilla"],
    previewItemId = 13468, -- Black Lotus
    texture = getExpansionTexturePath("wow.png"),
    expansionLevel = 0,
  },
  {
    major = 2,
    canonName = L["The Burning Crusade"],
    shortName = L["TBC"],
    previewItemId = 22787, -- Ragveil
    texture = getExpansionTexturePath("bc.png"),
    expansionLevel = 1,
  },
  {
    major = 3,
    canonName = L["Wrath of the Lich King"],
    shortName = L["WotLK"],
    previewItemId = 36907, -- Talandra's Rose
    texture = getExpansionTexturePath("wotlk.png"),
    expansionLevel = 2,
  },
  {
    major = 4,
    canonName = L["Cataclysm"],
    shortName = L["Cata"],
    previewItemId = 52985, -- Azshara's Veil
    texture = getExpansionTexturePath("cata.png"),
    expansionLevel = 3,
  },
  {
    major = 5,
    canonName = L["Mists of Pandaria"],
    shortName = L["MoP"],
    previewItemId = 72234, -- Green Tea Leaf
    texture = getExpansionTexturePath("mop.png"),
    expansionLevel = 4,
  },
  {
    major = 6,
    canonName = L["Warlords of Draenor"],
    shortName = L["WoD"],
    previewItemId = 109125, -- Fireweed
    texture = getExpansionTexturePath("wod.png"),
    expansionLevel = 5,
  },
  {
    major = 7,
    canonName = L["Legion"],
    shortName = L["Legion"],
    previewItemId = 124103, -- Foxflower
    texture = getExpansionTexturePath("legion.png"),
    expansionLevel = 6,
  },
  {
    major = 8,
    canonName = L["Battle for Azeroth"],
    shortName = L["BfA"],
    previewItemId = 152508, -- Winter's Kiss
    texture = getExpansionTexturePath("bfa.png"),
    expansionLevel = 7,
  },
  {
    major = 9,
    canonName = L["Shadowlands"],
    shortName = L["SL"],
    previewItemId = 168589, -- Marrowroot
    texture = getExpansionTexturePath("sl.png"),
    expansionLevel = 8,
    corrections = {
      168583, -- Widowbloom
      168586, -- Rising Glory
      168589, -- Marrowroot
      169701, -- Death Blossom
      171315, -- Nightshade
    }
  },
  {
    major = 10,
    canonName = L["Dragonflight"],
    shortName = L["DF"],
    previewItemId = 191464, -- Saxifrage
    texture = getExpansionTexturePath("df.png"),
    expansionLevel = 9,
  },
  {
    major = 11,
    canonName = L["The War Within"],
    shortName = L["WW"],
    previewItemId = 239691, -- Phantom Bloom
    texture = getExpansionTexturePath("ww.png"),
    expansionLevel = 10,
  },
  {
    major = 12,
    canonName = L["Midnight"],
    shortName = L["MN"],
    previewItemId = 236778, -- Mana Lily
    texture = getExpansionTexturePath("mn.png"),
    expansionLevel = 11,
  },
}

local ExpansionMixin = {}

---Check if this expansion is present on the current server
---@return boolean present True if the expansion is available
function ExpansionMixin:IsPresent()
  local clientExpansionLevel = GetClientDisplayExpansionLevel()
  return self.expansionLevel <= clientExpansionLevel
end

-- attach mixin
for _, expansion in ipairs(Private.Expansion.All) do
  Private.Table.Mixin(expansion, ExpansionMixin)
end

---@type table<number, Expansion>
local majorToExpansion = {}
for _, expansion in ipairs(Private.Expansion.All) do
  majorToExpansion[expansion.major] = expansion
end

---Get an expansion by its major version number
---@param major number The major version number (e.g., 1 for Classic, 10 for Dragonflight)
---@return Expansion|nil expansion The expansion data, or nil if not found
function Private.Expansion:GetExpansionFromMajor(major)
  return majorToExpansion[major]
end

---@type table<number, Expansion>
local correctionsTable = {}
for _, expansion in ipairs(Private.Expansion.All) do
  if expansion.corrections then
    for _, itemId in ipairs(expansion.corrections) do
      -- error fast and loud if already present, this is a mistake in source data, not runtime
      if correctionsTable[itemId] then
        error(string.format("Item id %d is already present in correctionsTable", itemId))
      end
      correctionsTable[itemId] = expansion
    end
  end
end

---Get the corrected expansion for an item ID
---@param itemId number The item ID to look up
---@return Expansion|nil expansion The corrected expansion, or nil if no correction exists
function Private.Expansion:GetCorrectedExpansionForItemId(itemId)
  return correctionsTable[itemId]
end
