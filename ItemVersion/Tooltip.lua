local _, Private = ...

Private.Tooltip = {}

---Check if the required key modifiers are being held down
---@return boolean areDown True if all required modifiers are pressed (or none are required)
local function keyModifiersAreDown()
  local profile = Private.Database.profile
  if profile.showOnShift and not IsShiftKeyDown() then
    return false
  end
  if profile.showOnControl and not IsControlKeyDown() then
    return false
  end
  if profile.showOnAlt and not IsAltKeyDown() then
    return false
  end
  -- this will only be able to be true on Mac clients
  if profile.showOnMeta and not IsMetaKeyDown() then
    return false
  end
  return true
end

---Extract the item ID from a tooltip
---@param tooltip table The tooltip frame
---@param data table|nil The tooltip data (mainline only)
---@return number|nil itemId The item ID, or nil if not found
local function getItemId(tooltip, data)
  -- mainline way
  if data then
    return data.id
  end

  -- classic way
  local name, link = tooltip:GetItem()
  if name and link then
    return tonumber(string.match(link, "item:(%d*)"))
  end
end

---Hook function called when a tooltip is shown
---@param tooltip table The tooltip frame
---@param data table|nil The tooltip data (mainline only)
local function hook(tooltip, data)
  -- GameTooltip is the one attached to the mouse
  -- ItemRefTooltip is the static one after clicking an item link
  if tooltip ~= GameTooltip and tooltip ~= ItemRefTooltip then
    return
  end

  if not keyModifiersAreDown() then
    return
  end

  local itemId = getItemId(tooltip, data)

  if not itemId then
    return
  end

  local profile = Private.Database.profile
  local lookup = Private.API.GetItemVersion(itemId, profile.applyCorrections)

  if not lookup then
    return
  end

  local line = Private.Color.WrapTextWithColor(
    Private.API.FormatTooltip(profile.tooltipFormat, lookup),
    profile.lineColor
  )

  tooltip:AddLine(line)
  tooltip:Show()
end

---Hook into the tooltip system to add item version information
function Private.Tooltip.HookTooltip()
  local hasOnTooltipSetItem = GameTooltip:HasScript("OnTooltipSetItem") and ItemRefTooltip:HasScript("OnTooltipSetItem")
  if hasOnTooltipSetItem then
    -- old way
    GameTooltip:HookScript("OnTooltipSetItem", hook)
    ItemRefTooltip:HookScript("OnTooltipSetItem", hook)
  elseif TooltipDataProcessor then
    -- new way
    TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item, hook)
  else
    error("ItemVersion: Unable to hook into tooltips!")
  end
end
