-- The @localization@ comments below are replaced with the translations held on
-- CurseForge when the addon is packaged, so the blocks they sit in are only
-- empty here in source.
--# selene: allow(empty_if)

local AddonName = ...

local AceLocale = LibStub("AceLocale-3.0")

-- Each locale is guarded with `if L then` rather than an early return.
-- NewLocale returns nil for every locale except the client's, and a return at
-- file scope would leave the rest of the file unread, so only the first locale
-- listed could ever load.
--
-- Translations belong on CurseForge, not here. Filling these blocks in by hand
-- would take the locale out of that pipeline.

local L = AceLocale:NewLocale(AddonName, "enUS", true)
L["Added in {expacIcon} ({versionTriple})"] = true
L["Addon Version"] = true
L["Apply version corrections"] = true
L["Battle for Azeroth"] = true
L["BfA"] = true
L["Build number only"] = true
L["Cata"] = true
L["Cataclysm"] = true
L["Color of the line of text in the tooltip"] = true
L["Correct the version for some items whose release version is different than their usable version."] = true
L["Customize the format of the item version information shown in tooltips."] = true
L["Description"] = true
L["DF"] = true
L["Dragonflight"] = true
L["Enable tooltip integration"] = true
L["Example"] = true
L["Expansion icon"] = true
L["Format Tokens"] = true
L["Full name of the expansion"] = true
L["Full version"] = true
L["Invalid item ID or link provided"] = true
L["ItemVersion does not support profile version %d, so your settings have been reset."] = true
L["Key Modifiers Needed to Show Info"] = true
L["Legion"] = true
L["Line Color"] = true
L["Lookup item ID or Link and print tooltip line"] = true
L["Major, minor, and patch version"] = true
L["Midnight"] = true
L["Mists of Pandaria"] = true
L["MN"] = true
L["MoP"] = true
L["Mouseover Preview"] = true
L["Must supply an item ID or link to lookup"] = true
L["No version information found for item ID %d"] = true
L["Open options"] = true
L["Platform"] = true
L["Profiles"] = true
L["Provide a template to format the tooltip line"] = true
L["Shadowlands"] = true
L["Short name of the expansion"] = true
L["Show item version info in tooltips when the %s key is held down."] = true
L["Show item version information in tooltips."] = true
L["Show this message"] = true
L["Show version info"] = true
L["SL"] = true
L["TBC"] = true
L["The Burning Crusade"] = true
L["The War Within"] = true
L["Token"] = true
L["Tooltip format"] = true
L["Usage: /itemversion <command>"] = true
L["Vanilla"] = true
L["Version Information"] = true
L["Warlords of Draenor"] = true
L["WoD"] = true
L["World of Warcraft"] = true
L["WotLK"] = true
L["WoW Build"] = true
L["WoW Build Date"] = true
L["WoW Version"] = true
L["Wrath of the Lich King"] = true
L["WW"] = true

L = AceLocale:NewLocale(AddonName, "deDE")
if L then
  --@localization(locale="deDE", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end

L = AceLocale:NewLocale(AddonName, "esES")
if L then
  --@localization(locale="esES", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end

L = AceLocale:NewLocale(AddonName, "esMX")
if L then
  --@localization(locale="esMX", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end

L = AceLocale:NewLocale(AddonName, "frFR")
if L then
  --@localization(locale="frFR", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end

L = AceLocale:NewLocale(AddonName, "itIT")
if L then
  --@localization(locale="itIT", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end

L = AceLocale:NewLocale(AddonName, "koKR")
if L then
  --@localization(locale="koKR", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end

L = AceLocale:NewLocale(AddonName, "ptBR")
if L then
  --@localization(locale="ptBR", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end

L = AceLocale:NewLocale(AddonName, "ruRU")
if L then
  --@localization(locale="ruRU", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end

L = AceLocale:NewLocale(AddonName, "zhCN")
if L then
  --@localization(locale="zhCN", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end

L = AceLocale:NewLocale(AddonName, "zhTW")
if L then
  --@localization(locale="zhTW", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@
end
