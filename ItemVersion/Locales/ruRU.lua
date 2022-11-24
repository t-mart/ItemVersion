local addonName = ...

local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "ruRU")
if not L then return end

L["Tooltip"] = "Всплывающая подсказка"
L["Added in"] = "Добавлен в"
L["Show prefix"] = "Показать приставку"
L["Prefix the tooltip line with a label"] = "Приставка строки всплывающей подсказки с меткой"
L["Prefix color"] = "Цвет приставки"
L["Prefix"] = "Приставка"
L["The color of the prefix"] = "Цветная приставка"
L["Use short expansion names"] = "Использовать короткие названия расширений"
L["Abbreviate the item's expansion"] = "Сократить расширение элемента"
L["Expansion color"] = "Цвет расширения"
L["The color of the expansion"] = "Цветное расширение"
L["Show version"] = "Показать версию"
L["Show the version in which the item was added"] = "Показать версию, в которой был добавлен элемент"
L["Version color"] = "Цвет версии"
L["The color of the version"] = "Цветная версия"
L["TBC"] = true
L["WotLK"] = true
L["Cata"] = true
L["MoP"] = true
L["WoD"] = true
L["BfA"] = true
L["SL"] = true
L["DF"] = true
L["Show for unknown items"] = "Показать неизвестные элементы"
L["Show the tooltip line even when the item is not in the database"] = "Показывать строку всплывающей подсказки, даже если элемент отсутствует в базе данных"
L["Modifier keys"] = "Клавиши-модификаторы"
L["Display the tooltip only when the selected modifier keys being are pressed. " ..
    "(No selections means always show.)"] = "Отображение всплывающей подсказки только при нажатии выбранных клавиш-модификаторов. " ..
	"(Если не выбрано, значит всегда показывать)"
L["Include community updates"] = "Включить обновления сообщества"
L["Including community updates changes some items' version/expansion to the one " ..
            "that players expect. For example, the herb [Marrowroot] was actually added towards " ..
            "the end of BfA in pre-release development, but was only obtainable in SL. With this " ..
            "option turned on, ItemVersion would report SL in this case, instead of BfA.\n\n" ..
            "Because the updates are non-canonical, the version number will be a placeholder one: " ..
            "the major part will be that of the new expansion, but the lesser parts will be zeroed.\n\n" ..
            "If you encounter an item that is not fixed by these updates, please consider " ..
            "reporting it to the project page."] = "Включение обновлений сообщества изменяет версию/расширение некоторых предметов на ту" ..
            ", которую ожидают игроки. Например, трава [Костяной корень] была фактически добавлена к " ..
            "концу BfA в предрелизной разработке, но получить ее можно было только в SL. При включении этой " ..
            "опции, ItemVersion будет сообщать в этом случае SL, вместо BfA.\n\n" ..
            "Поскольку обновления неканоничны, номер версии будет условным: " ..
            "большая часть будет принадлежать новому расширению, а меньшие части будут обнулены.\n\n" ..
            "Если Вы столкнулись с проблемой, которая не была исправлена этими обновлениями, пожалуйста, " ..
            "сообщите об этом на странице проекта."
L["Override canonical version/expansion with a community update."] = "Переопределить каноническую версию/расширение с помощью обновления сообщества"
-- эти expac-строки не известны в неосновной ветке, к сожалению
L["Battle for Azeroth"] = "Battle for Azeroth"
L["Shadowlands"] = "Shadowlands"
L["Dragonflight"] = "Dragonflight"

-- следующие строки НЕ нуждаются в переводе, поскольку Blizzard уже перевела их в GlobalsStrings,
-- но мы сохраняем их в этом файле для согласованности с другими строками.
-- Клиент будет определять их в соответствии с текущей локалью. И AceLocale будет использовать по умолчанию
-- эти назначения, если они не переопределены в любом другом файле локали.
L["Expansion"] = EXPANSION_FILTER_TEXT
L["Classic"] = EXPANSION_NAME0
L["The Burning Crusade"] = EXPANSION_NAME1
L["Wrath of the Lich King"] = EXPANSION_NAME2
L["Cataclysm"] = EXPANSION_NAME3
L["Mists of Pandaria"] = EXPANSION_NAME4
L["Warlords of Draenor"] = EXPANSION_NAME5
L["Legion"] = EXPANSION_NAME6
L["Preview"] = PREVIEW
L["Unknown"] = UNKNOWN
L["Version"] = GAME_VERSION_LABEL
L["SHIFT"] = SHIFT_KEY_TEXT
L["ALT"] = ALT_KEY_TEXT
L["CONTROL"] = CTRL_KEY_TEXT
L["Mode"] = MODE
