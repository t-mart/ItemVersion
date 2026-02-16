local AddonName = ...

local IsDevelopment = false
--@debug@
IsDevelopment = true
--@end-debug@

local AceLocale = LibStub("AceLocale-3.0")

local L = AceLocale:NewLocale(
    AddonName,
    "enUS",
    true,
    IsDevelopment -- During dev, don't error on missing translations (that will be added at build)
)
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
if not L then return end
--@localization(locale="deDE", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

L = AceLocale:NewLocale(AddonName, "esES")
if not L then return end
--@localization(locale="esES", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

L = AceLocale:NewLocale(AddonName, "esMX")
if not L then return end
--@localization(locale="esMX", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

L = AceLocale:NewLocale(AddonName, "frFR")
if not L then return end
--@localization(locale="frFR", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

L = AceLocale:NewLocale(AddonName, "itIT")
if not L then return end
--@localization(locale="itIT", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

L = AceLocale:NewLocale(AddonName, "koKR")
if not L then return end
--@localization(locale="koKR", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

L = AceLocale:NewLocale(AddonName, "ptBR")
if not L then return end
--@localization(locale="ptBR", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

L = AceLocale:NewLocale(AddonName, "ruRU")
if not L then return end
--@localization(locale="ruRU", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

L = AceLocale:NewLocale(AddonName, "zhCN")
if not L then return end
--@localization(locale="zhCN", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

L = AceLocale:NewLocale(AddonName, "zhTW")
if not L then return end
--@localization(locale="zhTW", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@