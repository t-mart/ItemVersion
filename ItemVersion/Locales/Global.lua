local addonName = ...

local L = LibStub("AceLocale-3.0"):GetLocale(addonName)
if not L then return end

-- Use these strings that are already translated to each locale from Blizzard.
L["Expansion"] = EXPANSION_FILTER_TEXT
L["Classic"] = EXPANSION_NAME0
L["The Burning Crusade"] = EXPANSION_NAME1
L["Wrath of the Lich King"] = EXPANSION_NAME2
L["Cataclysm"] = EXPANSION_NAME3
L["Mists of Pandaria"] = EXPANSION_NAME4
L["Warlords of Draenor"] = EXPANSION_NAME5
L["Legion"] = EXPANSION_NAME6
L["Preview"] = PREVIEW
L["Unknown"] = UNKNOWN
L["Version"] = GAME_VERSION_LABEL
L["SHIFT"] = SHIFT_KEY_TEXT
L["ALT"] = ALT_KEY_TEXT
L["CONTROL"] = CTRL_KEY_TEXT
L["CMD"] = CMD_KEY_TEXT
