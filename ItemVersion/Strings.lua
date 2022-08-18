local _, AddonTable = ...

local function notFound(_, key)
  return key;
 end

-- If field F has no value in table, return F
local L = setmetatable({}, {__index=notFound});

-- WoW localizes these for everyone
L["Version"] = GAME_VERSION_LABEL
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
L["Unknown"] = UNKNOWN
L["Item"] = HELPFRAME_ITEM_TITLE
L["Expansion"] = EXPANSION_FILTER_TEXT

-- Translations
-- Keep locale branch stubs for later use
local locale = GetLocale();
if locale == "deDE" then
  L[""] = ""
elseif locale == "enGB" then
  L[""] = ""
elseif locale == "enUS" then
  L[""] = ""
elseif locale == "esES" then
  L[""] = ""
elseif locale == "frFR" then
  L[""] = ""
elseif locale == "koKR" then
  L[""] = ""
elseif locale == "zhCN" then
  L[""] = ""
elseif locale == "zhTW" then
  L[""] = ""
elseif locale == "enCN" then
  L[""] = ""
elseif locale == "enTW" then
  L[""] = ""
elseif locale == "esMX" then
  L[""] = ""
elseif locale == "ruRU" then
  L[""] = ""
elseif locale == "ptBR" then
  L[""] = ""
elseif locale == "ptPT" then
  L[""] = ""
elseif locale == "itIT" then
  L[""] = ""
end

AddonTable.L = L;
