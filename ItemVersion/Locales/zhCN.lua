local addonName = ...

local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "zhCN")
if not L then
  return
end

L["Tooltip"] = "鼠标提示"
L["Added in"] = "添加于"
L["Show prefix"] = "显示前缀"
L["Prefix the tooltip line with a label"] = "在鼠标提示行中添加前缀"
L["Prefix color"] = "前缀颜色"
L["Prefix"] = "前缀"
L["The color of the prefix"] = "前缀文本的颜色"
L["Use short expansion names"] = "缩写版本名"
L["Abbreviate the item's expansion"] = "缩写物品的版本名称"
L["Expansion color"] = "版本名颜色"
L["The color of the expansion"] = "版本名称的颜色"
L["Show version"] = "显示版本号"
L["Show the version in which the item was added"] = "显示添加该物品的版本号"
L["Version color"] = "版本号颜色"
L["The color of the version"] = "版本号的颜色"
L["Show for unknown items"] = "显示未知物品"
L["Show the tooltip line even when the item is not in the database"] =
  "即使物品不在数据库中也显示鼠标提示"
L["Modifier keys"] = "组合键"
L["Display the tooltip only when the selected modifier keys being are pressed. (No selections means always show.)"] =
  "仅当选中的组合键被按下时显示鼠标提示（全不选即为始终显示）。"
L["Include community updates"] = "包含社区更新"
L["Including community updates changes some items' version/expansion to the one that players expect. For example, the herb [Marrowroot] was actually added towards the end of BfA in pre-release development, but was only obtainable in SL. With this option turned on, ItemVersion would report SL in this case, instead of BfA.\n\nBecause the updates are non-canonical, the version number will be a placeholder one: the major part will be that of the new expansion, but the lesser parts will be zeroed.\n\nIf you encounter an item that is not fixed by these updates, please consider reporting it to the project page."] =
  "使用社区修正的版本信息。例如[髓根草]在争霸艾泽拉斯最后的预发布版本中添加，但只能在暗影国度版本中获取。当启用该选项时，ItemVersion 会认为该物品添加自暗影国度而非争霸艾泽拉斯。\n\n因为这种修正是非官方的，主版本号将显示为修正后的，而其余部分将用0替代。\n\n如果你发现了需要修正的物品，可以考虑在项目页面中提交。"
L["Battle for Azeroth"] = "争霸艾泽拉斯"
L["Shadowlands"] = "暗影国度"
L["Dragonflight"] = "巨龙时代"
L["The War Within"] = "地心之战"
-- prevent AceLocale-3.0-6: ItemVersion: Missing entry for 'xxxxx'
L["经典旧世"] = true
L["燃烧的远征"] = true
L["巫妖王之怒"] = true
L["大地的裂变"] = true
L["熊猫人之谜"] = true
L["德拉诺之王"] = true
L["军团再临"] = true
L["争霸艾泽拉斯"] = true
L["暗影国度"] = true
L["巨龙时代"] = true
L["地心之战"] = true
