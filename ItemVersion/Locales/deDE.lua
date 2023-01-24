local addonName = ...

local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "deDE")
if not L then
  return
end

L["Tooltip"] = true
L["Added in"] = "Erweiterung:"
L["Show prefix"] = "[Erweiterung:] anzeigen"
L["Prefix the tooltip line with a label"] = "ergänze den Tooltip mit [Erweiterung:]"
L["Prefix color"] = "Farbe"
L["Prefix"] = "Vorsilbe [Erweiterung:]"
L["The color of the prefix"] = "Farbe Vorsilbe"
L["Use short expansion names"] = "kurze Erweiterungsnamen anzeigen"
L["Abbreviate the item's expansion"] = "Abkürzung der Erweiterung"
L["Expansion color"] = "Farbe"
L["The color of the expansion"] = "Farbe Erweiterung"
L["Show version"] = "Version anzeigen"
L["Show the version in which the item was added"] = "Zeigt die Version in welcher das Item hinzugefügt wurde"
L["Version color"] = "Farbe"
L["The color of the version"] = "Farbe Version"
L["TBC"] = true
L["WotLK"] = true
L["Cata"] = true
L["MoP"] = true
L["WoD"] = true
L["BfA"] = true
L["SL"] = true
L["DF"] = true
L["Show for unknown items"] = "zeigt den Tooltip auch für Unbekannte Items"
L["Show the tooltip line even when the item is not in the database"] =
  "Zeigen Sie die Tooltip-Zeile auch dann an, wenn sich das Item nicht in der Datenbank befindet"
L["Modifier keys"] = "Tastenkombination"
L["Display the tooltip only when the selected modifier keys being are pressed. " .. "(No selections means always show.)"] =
  "zeigt den Tooltip nur, wenn die ausgewählte Taste gedrückt wird. (bei keiner Auswahl wird der Tooltip immer angezeigt)"
L["Include community updates"] = "inklusive Community Update"
L["Including community updates changes some items' version/expansion to the one " .. "that players expect. For example, the herb [Marrowroot] was actually added towards " .. "the end of BfA in pre-release development, but was only obtainable in SL. With this " .. "option turned on, ItemVersion would report SL in this case, instead of BfA.\n\n" .. "Because the updates are non-canonical, the version number will be a placeholder one: " .. "the major part will be that of the new expansion, but the lesser parts will be zeroed.\n\n" .. "If you encounter an item that is not fixed by these updates, please consider " .. "reporting it to the project page."] = "Durch die Einbeziehung von Community-Updates wird die Version/Erweiterung einiger Gegenstände zu der Version/Erweiterung die die Spieler erwarten. "
  .. "Zum Beispiel wurde das Kraut [Markwurzel] tatsächlich gegen "
  .. "Ende von BfA hinzugefügt, war aber nur in SL erhältlich. Mit dieser "
  .. "würde ItemVersion in diesem Fall SL statt BfA melden."
  .. "Da es sich um keine regelmäßigen Updates handelt, wird die Versionsnummer ein Platzhalter sein: "
  .. "Der Hauptteil ist der der neuen Erweiterung, aber die kleineren Teile werden auf Null gesetzt.\n\n"
  .. "Wenn Sie auf ein Problem stoßen, das durch dieses Update nicht behoben wird, ziehen Sie bitte in Erwägung, "
  .. "es auf der Projektseite zu melden."
L["usage"] = "Verwendung"
L["subcommand"] = "Unterbefehl"
L["Available Subcommands"] = "Verfügbare Unterkommandos"
L["Opens the configuration window"] = "öffnet das Konfigurationsfenster"
L["Opens a window with information to assist in creating an issue"] =
  "Öffnet ein Fenster mit Informationen, die bei der Erstellung eines Problems helfen"
L["Displays the version of ItemVersion"] = "zeigt die Version von ItemVersion"
L["Shows this help"] = "zeigt diese Hilfe"
L["%s Issue Information"] = "%s Informationen zur Ausgabe"
L["Copy and paste this data when making a new issue for ItemVersion."] =
  "Kopieren Sie diese Daten und fügen Sie sie ein, wenn Sie eine neue Ausgabe für ItemVersion erstellen."
L["Client flavor and version"] = "Client-Variante und Version"
L["ItemVersion version"] = "Version von ItemVersion"
L["Platform"] = true
L["Issue URL"] = "Ausgabeadresse"

-- these expac strings aren't known in non-mainline, unfortunately
L["Battle for Azeroth"] = "Battle for Azeroth"
L["Shadowlands"] = "Shadowlands"
L["Dragonflight"] = "Dragonflight"
