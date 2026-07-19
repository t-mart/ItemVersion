local _, Private = ...

-- Upvalued for the tooltip render and modifier keypress paths
local IsShiftKeyDown = IsShiftKeyDown
local IsControlKeyDown = IsControlKeyDown
local IsAltKeyDown = IsAltKeyDown
local IsMetaKeyDown = IsMetaKeyDown
local tonumber = tonumber
local match = string.match

Private.Tooltip = {}

-- Frames we modify, resolved once in HookTooltip. hookedFrames drives the modifier
-- refresh; isHookedFrame is the filter the render hook applies, since the mainline
-- post-call is global and fires for every tooltip in the game.
local hookedFrames = {}
local isHookedFrame = {}

-- Dedupe guard. OnTooltipSetItem and the mainline post-call can each fire more than
-- once for the same tooltip contents before a clear (comparison tooltips and
-- re-sets are common sources), which would add our line twice. We stamp a frame when
-- we add the line and clear the stamp on OnTooltipCleared, so the next fill can add
-- it again.
local lineAddedTo = {}

-- MODIFIER_STATE_CHANGED reports each physical key, so both sides of a modifier
-- map to the one profile key that gates it.
local MODIFIER_PROFILE_KEYS = {
  LSHIFT = "showOnShift",
  RSHIFT = "showOnShift",
  LCTRL = "showOnControl",
  RCTRL = "showOnControl",
  LALT = "showOnAlt",
  RALT = "showOnAlt",
  LMETA = "showOnMeta",
  RMETA = "showOnMeta",
}

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
    return tonumber(match(link, "item:(%d+)"))
  end
end

---Hook function called when a tooltip is shown
---@param tooltip table The tooltip frame
---@param data table|nil The tooltip data (mainline only)
local function hook(tooltip, data)
  local profile = Private.Database.profile
  if not profile.enableTooltip then
    return
  end

  if not isHookedFrame[tooltip] then
    return
  end

  -- Already stamped this fill; adding again would duplicate the line.
  if lineAddedTo[tooltip] then
    return
  end

  if not keyModifiersAreDown() then
    return
  end

  local itemId = getItemId(tooltip, data)

  if not itemId then
    return
  end
  local lookup = Private.API.GetItemVersion(itemId, profile.applyCorrections)

  if not lookup then
    return
  end

  local line = Private.Color.WrapTextWithColor(lookup:Format(profile.tooltipFormat), profile.lineColor)

  lineAddedTo[tooltip] = true
  tooltip:AddLine(line)
  tooltip:Show()
end

---Reset the dedupe guard when a tooltip is wiped, so the next fill can add the line
---@param tooltip table The tooltip frame
local function onTooltipCleared(tooltip)
  lineAddedTo[tooltip] = nil
end

---Rebuild a tooltip in place, so the version line can appear or disappear
---
---A tooltip line cannot be removed once added, so reacting to a modifier means
---rebuilding the whole tooltip rather than editing it.
---@param tooltip table The tooltip frame
local function refresh(tooltip)
  if not tooltip:IsShown() then
    return
  end

  -- Only item tooltips carry our line. Rebuilding a unit or spell tooltip on
  -- every keypress would be work at best and a flicker at worst.
  local _, link = tooltip:GetItem()
  if not link then
    return
  end

  if tooltip.RefreshData then
    tooltip:RefreshData()
    return
  end

  -- Flavors without the tooltip data API cannot replay the call that populated
  -- the tooltip, so re-set it from the link. This is lossy: whatever the owner
  -- supplied beyond the item itself, such as a stack count or bind state, is not
  -- in the link and does not survive the rebuild. Hence the fallback.
  tooltip:SetHyperlink(link)
end

---Refresh open tooltips when a modifier the user gates on is pressed or released
---@param key string The modifier key name, such as LSHIFT
local function onModifierStateChanged(key)
  local profile = Private.Database.profile
  if not profile.enableTooltip then
    return
  end

  -- A modifier the profile does not gate on cannot change what the line shows,
  -- and with no modifiers set at all the line is always up. Either way, leave
  -- the tooltip alone.
  local profileKey = MODIFIER_PROFILE_KEYS[key]
  if not profileKey or not profile[profileKey] then
    return
  end

  for _, tooltip in ipairs(hookedFrames) do
    refresh(tooltip)
  end
end

---Call fn once for each frame that exists, tolerating the nil holes that appear
---because some of these frames do not exist on every flavor. A plain table literal
---plus ipairs would stop at the first missing frame, so pass them as varargs.
---@param fn fun(frame: table)
local function forEachPresentFrame(fn, ...)
  for i = 1, select("#", ...) do
    local frame = select(i, ...)
    if frame then
      fn(frame)
    end
  end
end

---Hook into the tooltip system to add item version information
function Private.Tooltip.HookTooltip()
  -- GameTooltip is the one attached to the mouse; ItemRefTooltip is the static one
  -- after clicking an item link; the ShoppingTooltip pair renders the currently
  -- equipped item(s) alongside a hovered one, and the ItemRef variants do the same
  -- off a chat link.
  forEachPresentFrame(
    function(frame)
      table.insert(hookedFrames, frame)
      isHookedFrame[frame] = true
    end,
    GameTooltip,
    ItemRefTooltip,
    ShoppingTooltip1,
    ShoppingTooltip2,
    ItemRefShoppingTooltip1,
    ItemRefShoppingTooltip2
  )

  if GameTooltip:HasScript("OnTooltipSetItem") then
    -- old way: a per-frame render script
    for _, frame in ipairs(hookedFrames) do
      if frame:HasScript("OnTooltipSetItem") then
        frame:HookScript("OnTooltipSetItem", hook)
      end
    end
  elseif TooltipDataProcessor then
    -- new way: one global post-call for every item tooltip. hook filters to the
    -- frames we care about via isHookedFrame.
    TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item, hook)
  else
    error("ItemVersion: Unable to hook into tooltips!")
  end

  -- Reset the dedupe guard whenever a frame's contents are wiped.
  for _, frame in ipairs(hookedFrames) do
    if frame:HasScript("OnTooltipCleared") then
      frame:HookScript("OnTooltipCleared", onTooltipCleared)
    end
  end

  -- The compare tooltips are populated through SetCompareItem, which does not
  -- reliably emit an item render on every flavor, so the hooks above can miss them.
  -- Hook the method directly so the line still lands; the dedupe guard keeps this
  -- from doubling up on flavors where the render does fire.
  forEachPresentFrame(function(frame)
    if frame.SetCompareItem then
      hooksecurefunc(frame, "SetCompareItem", function(self)
        hook(self, nil)
      end)
    end
  end, ShoppingTooltip1, ShoppingTooltip2, ItemRefShoppingTooltip1, ItemRefShoppingTooltip2)

  local watcher = CreateFrame("Frame")
  watcher:RegisterEvent("MODIFIER_STATE_CHANGED")
  watcher:SetScript("OnEvent", function(_, _, key)
    onModifierStateChanged(key)
  end)
end
