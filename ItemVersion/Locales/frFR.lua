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
L["Show for unknown items"] = "Afficher pour les objets inconnus"
L["Show the tooltip line even when the item is not in the database"] = "Afficher même quand l'objet n'est pas dans la base de données"
L["Modifier keys"] = "Touches de modification"
L["Display the tooltip only when the selected modifier keys being are pressed. (No selections means always show.)"] =
  "Affiche l’info-bulle uniquement lorsque vous appuyez sur les touches de modification sélectionnées. (Pas de sélections, toujours affiché.)"
L["Include community updates"] = "Inclure les mise à jours de la communauté"
L["Including community updates changes some items' version/expansion to the one that players expect. For example, the herb [Marrowroot] was actually added towards the end of BfA in pre-release development, but was only obtainable in SL. With this option turned on, ItemVersion would report SL in this case, instead of BfA.\n\nBecause the updates are non-canonical, the version number will be a placeholder one: the major part will be that of the new expansion, but the lesser parts will be zeroed.\n\nIf you encounter an item that is not fixed by these updates, please consider reporting it to the project page."] =
  "L’inclusion des mises à jour de la communauté modifie la version/extension de certains objets pour qu’elle corresponde à celle attendue par les joueurs. Par exemple, l’herbe [Courgineuse] a été ajoutée vers la fin de BfA dans les fichiers du pré-patch, mais n’était disponible qu’a SL. Lorsque cette option est activée, ItemVersion indique SL dans ce cas, au lieu de BfA.\n\nÉtant donné que ces mises à jour ne sont pas canon, le numéro de version sera un numéro d’espace réservé : la partie principale sera celle de la nouvelle extension, mais les parties inférieures seront mises à zéro.\n\nSi vous rencontrez un objet qui n’est pas corrigé par ces mises à jour, veuillez envisager de le signaler sur la page du projet."
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
