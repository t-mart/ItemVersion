local _, AddonTable = ...

local function notFound(_, key)
  return key;
 end

local L = setmetatable({}, {__index=notFound});

local locale = GetLocale();

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

if locale== "deDE" then
  -- L["Something in english"] = "Something in german"
  L[""] = L[""]
elseif locale == "esES" then
  L[""] = L[""]
elseif locale == "esMX" then
  L[""] = L[""]
elseif locale == "frFR" then
  L[""] = L[""]
elseif locale == "itIT" then
  L[""] = L[""]
elseif locale == "koKR" then
  L[""] = L[""]
elseif locale == "ptBR" then
  L[""] = L[""]
elseif locale == "ruRU" then
  L[""] = L[""]
elseif locale == "zhCN" then
  L[""] = L[""]
elseif locale == "zhTW" then
  L[""] = L[""]
end

AddonTable.L = L;
