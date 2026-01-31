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
L["BC"] = true
L["WotLK"] = true
L["Cata"] = true
L["MoP"] = true
L["WoD"] = true
L["BfA"] = true
L["SL"] = true
L["DF"] = true
L["WW"] = true
L["MN"] = true
L["Show for unknown items"] = true
L["Show the tooltip line even when the item is not in the database"] = true
L["Modifier keys"] = true
L["Display the tooltip only when the selected modifier keys being are pressed. (No selections means always show.)"] =
    true
L["Include community updates"] = true
L["Correct the version for some items"] = true
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
L["Show build number"] = true
L["Include or omit the build number in the tooltip"] = true
L["Added in {expacIcon} ({versionTriple})"] = true
L["Apply version corrections"] = true
L["Correct the version for some items whose release version is different than their usable version. (Keep enabled unless you have a specific reason not to.)"] = true
L["Tooltip format string"] = true
L["Provide a template to format the tooltip line"] = true
L["Colors"] = true
L["Color to use for expansion names in tooltips."] = true
L["Token Color"] = true
L["Color to use for versions in tooltips."] = true
L["Colors"] = true
L["Key Modifiers Needed to Show Info"] = true
L["Show item version info in tooltips when the %s key is held down."] = true
L["Customize the format of the item version information shown in tooltips."] = true
L["Token"] = true
L["Description"] = true
L["Example"] = true
L["Canonical name of the expansion"] = true
L["Short name of the expansion"] = true
L["Full version"] = true
L["Major, minor, and patch version"] = true
L["Build number only"] = true
L["Expansion icon"] = true
L["Format String Tokens"] = true
L["Color to use for tokens in tooltips."] = true
L["Tooltip format"] = true
L["Mouseover Preview"] = true

-- these expac strings aren't known in non-mainline, unfortunately
L["Shadowlands"] = true
L["Dragonflight"] = true
L["The War Within"] = true
L["Midnight"] = true
