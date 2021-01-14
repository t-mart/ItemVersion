local version_label_text = "Version"
local expac_label_text = "Expac"

local function tooltipString(itemId)
  local version = ItemVersion.getItemVersion(itemId)
  local expac = ItemVersion.getItemExpac(itemId)

  local left = format('|cFFCA3C3C%s|r %s', version_label_text, ItemVersion.versionString(version))
  local right = format('|cFFCA3C3C%s|r %s', expac_label_text, expac.canonName)

  return left, right
end

local function OnTooltipSetItem(tooltip)
  local _, link = tooltip:GetItem()

  -- happens when looking at crafting spells at profession trainer, despite this function
  -- only being called on item tooltips: blizzard strangeness.
  if not link then
    return
  end

  local itemId = tonumber(strmatch(link, ':(%w+)'))
  local left, right = tooltipString(itemId)
  tooltip:AddDoubleLine(left, right);
  tooltip:Show()
end

-- Not reliable, but I want this info at the bottom of the tooltip, and the order of addons' stuff
-- appearing in the tooltip is the same as the order of those addons calling HookScript. So,
-- delaying our call puts our stuff very likely at the end of the tooltip.
C_Timer.After(5, function()
  GameTooltip:HookScript("OnTooltipSetItem", OnTooltipSetItem)
end)
