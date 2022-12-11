local addonName = ...

local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "koKR")
if not L then
  return
end

L["Tooltip"] = "툴팁"
L["Added in"] = "추가: "
L["Show prefix"] = "접두사 표시"
L["Prefix the tooltip line with a label"] = "확장팩 정보에 접두사 표시"
L["Prefix color"] = "접두사 색상"
L["Prefix"] = "접두사"
L["The color of the prefix"] = "접두사 색상 설정"
L["Use short expansion names"] = "확장팩 이름을 짧게 표시"
L["Abbreviate the item's expansion"] = "확장팩 이름을 단축어로 표시합니다."
L["Expansion color"] = "확장팩 색상"
L["The color of the expansion"] = "확장팩 색상 설정"
L["Show version"] = "버전 표시"
L["Show the version in which the item was added"] = "아이템이 추가된 버전을 표시합니다."
L["Version color"] = "버전 색상"
L["The color of the version"] = "버전 색상 설정"
L["TBC"] = "불성"
L["WotLK"] = "리분"
L["Cata"] = "대격변"
L["MoP"] = "판다"
L["WoD"] = "드군"
L["BfA"] = "격아"
L["SL"] = "어둠땅"
L["DF"] = "용군단"
L["Show for unknown items"] = "미확인 아이템 표시"
L["Show the tooltip line even when the item is not in the database"] =
  "DB에 없는 아이템을 툴팁에 표시합니다."
L["Modifier keys"] = "기능키"
L["Display the tooltip only when the selected modifier keys being are pressed. (No selections means always show.)"] =
  "툴팁에 정보를 표시할 때 기능키를 눌러야 합니다. (선택하지 않으면 기본적으로 모두 보입니다.)"
L["Include community updates"] = "커뮤니티 업데이트 포함"
L["Including community updates changes some items' version/expansion to the one that players expect. For example, the herb [Marrowroot] was actually added towards the end of BfA in pre-release development, but was only obtainable in SL. With this option turned on, ItemVersion would report SL in this case, instead of BfA.\n\nBecause the updates are non-canonical, the version number will be a placeholder one: the major part will be that of the new expansion, but the lesser parts will be zeroed.\n\nIf you encounter an item that is not fixed by these updates, please consider reporting it to the project page."] =
  "커뮤니티 업데이트를 포함하면 일부 아이템의 버전 및 확장팩 정보가 변경됩니다.예를 들어 [골수뿌리]라는 약초 아이템은 격아 말기에 추가되었지만, 실제로는 어둠땅에서만 채집할 수 있습니다.그래서 이 설정을 사용하면 어둠땅에 추가된 아이템으로 표시됩니다.이 업데이트는 비공식이기 때문에 버전표시가 한자리 입니다. 주요 부분은 새로운 확장팩의 버전이지만, 더 작게 되면 0이 됩니다.이러한 업데이트로 변경되지 않는 아이템들이 있다면 프로젝트 페이지에 보고해주세요."
L["usage"] = "사용법"
L["subcommand"] = "명령어"
L["Available Subcommands"] = "명령어를 사용합니다."
L["Opens the configuration window"] = "설정창을 엽니다."
L["Opens a window with information to assist in creating an issue"] =
  "이슈되는 내용의 도움이 될만한 정보 창을 엽니다."
L["Displays the version of ItemVersion"] = "ItemVersion의 버전을 표시합니다."
L["Shows this help"] = "이 도움말을 표시합니다."
L["%s Issue Information"] = "%s 이슈 정보"
L["Copy and paste this data when making a new issue for ItemVersion."] =
  "ItemVersion에 대한 새 이슈는 이 데이터를 복사하여 붙여넣기 하세요."

-- these expac strings aren't known in non-mainline, unfortunately
L["Battle for Azeroth"] = "격전의 아제로스"
L["Shadowlands"] = "어둠땅"
L["Dragonflight"] = "용군단"
