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
--@localization(locale="enUS", format="lua_additive_table", same-key-is-true=true, handle-subnamespaces="concat")@

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