local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)

Private.Expansion = {}

local function getExpansionTexturePath(fileName)
  return "Interface\\AddOns\\" .. AddonName .. "\\Media\\Images\\Expansions\\" .. fileName
end

Private.Expansion.ALL = {
  {
    major = 1,
    canonName = L["Classic"],
    shortName = L["Classic"],
    previewItemId = 13468, -- Black Lotus
    texture = getExpansionTexturePath("wow.png"),
  },
  {
    major = 2,
    canonName = L["The Burning Crusade"],
    shortName = L["BC"],
    previewItemId = 22787, -- Ragveil
    texture = getExpansionTexturePath("bc.png"),
  },
  {
    major = 3,
    canonName = L["Wrath of the Lich King"],
    shortName = L["WotLK"],
    previewItemId = 36907, -- Talandra's Rose
    texture = getExpansionTexturePath("wotlk.png"),
  },
  {
    major = 4,
    canonName = L["Cataclysm"],
    shortName = L["Cata"],
    previewItemId = 52985, -- Azshara's Veil
    texture = getExpansionTexturePath("cata.png"),
  },
  {
    major = 5,
    canonName = L["Mists of Pandaria"],
    shortName = L["MoP"],
    previewItemId = 72234, -- Green Tea Leaf
    texture = getExpansionTexturePath("mop.png"),
  },
  {
    major = 6,
    canonName = L["Warlords of Draenor"],
    shortName = L["WoD"],
    previewItemId = 109125, -- Fireweed
    texture = getExpansionTexturePath("wod.png"),
  },
  {
    major = 7,
    canonName = L["Legion"],
    shortName = L["Legion"],
    previewItemId = 124103, -- Foxflower
    texture = getExpansionTexturePath("legion.png"),
  },
  {
    major = 8,
    canonName = L["Battle for Azeroth"],
    shortName = L["BfA"],
    previewItemId = 152508, -- Winter's Kiss
    texture = getExpansionTexturePath("bfa.png"),
  },
  {
    major = 9,
    canonName = L["Shadowlands"],
    shortName = L["SL"],
    previewItemId = 168589, -- Marrowroot
    texture = getExpansionTexturePath("sl.png"),
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
  },
  {
    major = 11,
    canonName = L["The War Within"],
    shortName = L["WW"],
    previewItemId = 239691, -- Phantom Bloom
    texture = getExpansionTexturePath("ww.png"),
  },
  {
    major = 12,
    canonName = L["Midnight"],
    shortName = L["MN"],
    previewItemId = 236778, -- Mana Lily
    texture = getExpansionTexturePath("mn.png"),
  },
}

local majorToExpansion = {}
for _, expansion in ipairs(Private.Expansion.ALL) do
  majorToExpansion[expansion.major] = expansion
end

function Private.Expansion:GetExpansionFromMajor(major)
  return majorToExpansion[major]
end

local correctionsTable = {}
for _, expansion in ipairs(Private.Expansion.ALL) do
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

function Private.Expansion:GetCorrectedExpansionForItemId(itemId)
  return correctionsTable[itemId]
end
