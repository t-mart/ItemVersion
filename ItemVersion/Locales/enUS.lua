local addonName = ...

local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "enUS", true)
if not L then
  return
end

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
L["Display the tooltip only when the selected modifier keys being are pressed. (No selections means always show.)"] =
  true
L["Include community updates"] = true
L["Including community updates changes some items' version/expansion to the one that players expect. For example, the herb [Marrowroot] was actually added towards the end of BfA in pre-release development, but was only obtainable in SL. With this option turned on, ItemVersion would report SL in this case, instead of BfA.\n\nBecause the updates are non-canonical, the version number will be a placeholder one: the major part will be that of the new expansion, but the lesser parts will be zeroed.\n\nIf you encounter an item that is not fixed by these updates, please consider reporting it to the project page."] =
  true
L["usage"] = true
L["subcommand"] = true
L["Available Subcommands"] = true
L["Opens the configuration window"] = true
L["Opens a window with information to assist in creating an issue"] = true
L["Displays the version of ItemVersion"] = true
L["Shows this help"] = true
L["%s Issue Information"] = true
L["Copy and paste this data when making a new issue for ItemVersion."] = true
L["Client flavor and version"] = true
L["ItemVersion version"] = true
L["Platform"] = true
L["Issue URL"] = true

-- these expac strings aren't known in non-mainline, unfortunately
L["Battle for Azeroth"] = true
L["Shadowlands"] = true
L["Dragonflight"] = true
