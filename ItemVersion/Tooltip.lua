local _, AddonTable = ...

local versionLabelText = "Version"
local expacLabelText = "Expansion"

local function versionString(version)
  return format("%d.%d.%d.%d", version.major, version.minor, version.patch,
                version.build)
end

local function tooltipString(itemId)
  local version = AddonTable.getItemVersion(itemId)
  local left, right
  if version ~= nil then
    left = format("|cFF1F77B4%s|r %s", versionLabelText, versionString(version))
    right = format("|cFF1F77B4%s|r %s", expacLabelText,
                   AddonTable.getVersionExpac(version).canonName)
  else
    left = format("|cFF989898%s %s|r ", "ItemId", itemId)
    right = format("|cFF989898%s",
                   "Not in ItemVersion")
  end
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

  local itemId = tonumber(strmatch(link, "item:(%d*)"))

  -- will be nil for crafting reagents in profession window and legion artifacts
  if not itemId then
    return
  end

  local left, right = tooltipString(itemId)
  tooltip:AddDoubleLine(left, right)
  tooltip:Show()
end

-- Not reliable, but I want this info at the bottom of the tooltip, and the
-- order of addons' stuff appearing in the tooltip is the same as the order of
-- those addons calling HookScript. So, delaying our call puts our stuff very
-- likely at the end of the tooltip.
C_Timer.After(3, function()
  GameTooltip:HookScript("OnTooltipSetItem", OnTooltipSetItem)
end)
