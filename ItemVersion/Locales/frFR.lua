local addonName = ...

local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "frFR")
if not L then
  return
end

L["Tooltip"] = "Infobulle"
L["Added in"] = "Ajouté avec"
L["Show prefix"] = "Voir le préfixe"
L["Prefix the tooltip line with a label"] = "Ajoute un préfixe à l'infobulle"
L["Prefix color"] = "Couleur du préfixe"
L["Prefix"] = "Préfixe"
L["The color of the prefix"] = "La couleur du préfixe"
L["Use short expansion names"] = "Utiliser les noms d'extension abrégés"
L["Abbreviate the item's expansion"] = "Extensions abrégées"
L["Expansion color"] = "Couleur d'extension"
L["The color of the expansion"] = "La couleur de l'extension"
L["Show version"] = "Voir la version"
L["Show the version in which the item was added"] = "Affiche dans quelle version l'objet à été ajouté"
L["Version color"] = "Couleur de version"
L["The color of the version"] = "La couleur de la version"
L["TBC"] = true
L["WotLK"] = true
L["Cata"] = true
L["MoP"] = true
L["WoD"] = true
L["BfA"] = true
L["SL"] = true
L["DF"] = true
L["WW"] = true
L["Show for unknown items"] = "Afficher pour les objets inconnus"
L["Show the tooltip line even when the item is not in the database"] = "Afficher même quand l'objet n'est pas dans la base de données"
L["Modifier keys"] = "Touches de modification"
L["Display the tooltip only when the selected modifier keys being are pressed. (No selections means always show.)"] =
  "Affiche l’infobulle uniquement lorsque vous appuyez sur les touches de modification sélectionnées. (Pas de sélections, toujours affiché.)"
L["Include community updates"] = "Inclure les mise à jours de la communauté"
L["Correct the version for some items"] = "Corrige la version de certains objets"
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
L["Show build number"] = "Afficher le numéro de build"
L["Include or omit the build number in the tooltip"] = "Inclure ou omettre le numéro de build dans l’infobulle"

-- these expac strings aren't known in non-mainline, unfortunately
L["Shadowlands"] = true
L["Dragonflight"] = true
L["The War Within"] = true
