local addonName = ...

ItemVersion = LibStub("AceAddon-3.0"):GetAddon(addonName)
local L = LibStub("AceLocale-3.0"):GetLocale(addonName)

local majorToExpac = {
  [1] = { canonName = L["Classic"], shortName = L["Classic"], },
  [2] = { canonName = L["The Burning Crusade"], shortName = L["TBC"], },
  [3] = { canonName = L["Wrath of the Lich King"], shortName = L["WotLK"], },
  [4] = { canonName = L["Cataclysm"], shortName = L["Cata"], },
  [5] = { canonName = L["Mists of Pandaria"], shortName = L["MoP"], },
  [6] = { canonName = L["Warlords of Draenor"], shortName = L["WoD"], },
  [7] = { canonName = L["Legion"], shortName = L["Legion"], },
  [8] = { canonName = L["Battle for Azeroth"], shortName = L["BfA"], },
  [9] = { canonName = L["Shadowlands"], shortName = L["SL"], },
  [10] = { canonName = L["Dragonflight"], shortName = L["DF"], },
}

function ItemVersion:getExpacFromMajor(major)
  return majorToExpac[major]
end