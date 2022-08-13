local versionLabelText = "Version"
local expacLabelText = "Expansion"

local function versionString(version)
  return format("%d.%d.%d.%d", version.major, version.minor, version.patch,
                version.build)
end

local function tooltipString(version)
  local left = format('|cFFCA3C3C%s|r %s', versionLabelText,
                      versionString(version))
  local right = format('|cFFCA3C3C%s|r %s', expacLabelText,
                       ItemVersion.getVersionExpac(version).canonName)
  return left, right
end

local function OnTooltipSetItem(tooltip)
  -- blizzard broke tooltips in some cases. we return out of this function in
  -- those cases. These are known issues
  local _, link = tooltip:GetItem()

  -- will be nil for crafting spells at profession trainer vendor window
  if not link then
    return
  end

  local itemId = tonumber(strmatch(link, 'item:(%d*)'))

  -- will be nil for crafting reagents in profession window and legion artifacts
  if not itemId then
    return
  end

  local version = ItemVersion.getVersion(itemId)

  -- if item is not in DB
  if not version then
	local left = format('|c80CA3C3C%s|r %s', 'ItemId', itemId)
	local right = format('|c80CA3C3C%s',
                       'Not in ItemVersion')
	tooltip:AddDoubleLine(left, right)
	tooltip:Show()
    return
  end

  local left, right = tooltipString(version)
  tooltip:AddDoubleLine(left, right)
  tooltip:Show()
end

-- Not reliable, but I want this info at the bottom of the tooltip, and the
-- order of addons' stuff appearing in the tooltip is the same as the order of
-- those addons calling HookScript. So, delaying our call puts our stuff very
-- likely at the end of the tooltip.
C_Timer.After(5, function()
  GameTooltip:HookScript("OnTooltipSetItem", OnTooltipSetItem)
end)
