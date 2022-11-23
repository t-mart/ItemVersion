local addonName = ...

local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "enUS", true)
if not L then return end

L["Tooltip"] = true
L["Added in"] = true
L["Show prefix"] = true
L["Prefix the tooltip line with a label"] = true
L["Prefix color"] = true
L["Prefix"] = true
L["The color of the prefix"] = true
L["Use short expansion names"] = true
L["Abbreviate the item's expansion"] = true
L["Expansion color"] = true
L["The color of the expansion"] = true
L["Show version"] = true
L["Show the version in which the item was added"] = true
L["Version color"] = true
L["The color of the version"] = true
L["TBC"] = true
L["WotLK"] = true
L["Cata"] = true
L["MoP"] = true
L["WoD"] = true
L["BfA"] = true
L["SL"] = true
L["DF"] = true
L["Show for unknown items"] = true
L["Show the tooltip line even when the item is not in the database"] = true
L["Modifier keys"] = true
L["Display the tooltip only when the selected modifier keys being are pressed. (No selections means always show.)"] = true
L["Include community updates"] = true
L["Override canonical version/expansion with a community update."] = true

-- the following do NOT need translation because Blizzard already has in GlobalsStrings,
-- but we keep them in this file for consistency with other strings.
-- The client will define these according the the current locale. And, AceLocale will default to
-- these assignments if they are not overriden in any other locale file.
L["Expansion"] = EXPANSION_FILTER_TEXT
L["Classic"] = EXPANSION_NAME0
L["The Burning Crusade"] = EXPANSION_NAME1
L["Wrath of the Lich King"] = EXPANSION_NAME2
L["Cataclysm"] = EXPANSION_NAME3
L["Mists of Pandaria"] = EXPANSION_NAME4
L["Warlords of Draenor"] = EXPANSION_NAME5
L["Legion"] = EXPANSION_NAME6
L["Battle for Azeroth"] = EXPANSION_NAME7
L["Shadowlands"] = EXPANSION_NAME8
L["Dragonflight"] = EXPANSION_NAME9
L["Preview"] = PREVIEW
L["Unknown"] = UNKNOWN
L["Version"] = GAME_VERSION_LABEL
L["SHIFT"] = SHIFT_KEY_TEXT
L["ALT"] = ALT_KEY_TEXT
L["CONTROL"] = CTRL_KEY_TEXT
L["Mode"] = MODE
