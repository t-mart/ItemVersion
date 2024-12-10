local addonName = ...

local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "ruRU")
if not L then
  return
end

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
L["WW"] = true
L["Show for unknown items"] = "Показать неизвестные элементы"
L["Show the tooltip line even when the item is not in the database"] = "Показывать строку всплывающей подсказки, даже если элемент отсутствует в базе данных"
L["Modifier keys"] = "Клавиши-модификаторы"
L["Display the tooltip only when the selected modifier keys being are pressed. (No selections means always show.)"] = "Отображение всплывающей подсказки только при нажатии выбранных клавиш-модификаторов. (Если не выбрано, значит всегда показывать)"
L["Include community updates"] = "Включить обновления сообщества"
L["Correct the version for some items"] = "Исправить версию для некоторых элементов"
L["usage"] = "использование"
L["subcommand"] = "субкоманда"
L["Available Subcommands"] = "Доступные субкоманды"
L["Opens the configuration window"] = "Открывает окно конфигурации"
L["Opens a window with information to assist in creating an issue"] = "Открывает окно с информацией для помощи в создании нового отчёта об ошибке"
L["Displays the version of ItemVersion"] = "Отображает версию ItemVersion"
L["Shows this help"] = "Показывает эту справку"
L["%s Issue Information"] = "%s Информация о проблеме"
L["Copy and paste this data when making a new issue for ItemVersion."] = "Скопируйте и вставьте эти данные при создании нового отчёта об ошибке для ItemVersion."
L["Client flavor and version"] = "Тип и версия клиента"
L["ItemVersion version"] = "Версия аддона ItemVersion"
L["Platform"] = "Платформа"
L["Issue URL"] = "URL-ссылка для отчёта об ошибке"
L["Show build number"] = "Показать номер сборки"
L["Include or omit the build number in the tooltip"] = "Включить или исключить номер сборки из подсказки"

-- эти expac-строки не известны в неосновной ветке, к сожалению
L["Shadowlands"] = "Shadowlands"
L["Dragonflight"] = "Dragonflight"
L["The War Within"] = "The War Within"
