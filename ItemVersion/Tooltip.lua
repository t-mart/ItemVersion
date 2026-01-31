local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)
local API = Private.API
local Expansion = Private.Expansion
local Database = Private.Database

Private.Tooltip = {}

-- function Private.Tooltip:New(db)
--   local t = {
--     db = db,
--   }

--   return Util.Mixin(t, TooltipMixin)
-- end

local function WrapTextInColor(text, color)
  local hex = ("|c%.2x%.2x%.2x%.2x"):format(
    floor((color.a or 1) * 255),
    floor(color.r * 255),
    floor(color.g * 255),
    floor(color.b * 255)
  )
  return WrapTextInColorCode(text, hex)
end

local function MakeItemTextureString(itemId)
  return format("|T%d:0|t", itemId)
end

local function areKeyModifiersDown()
  if Database:GetValue("isShowOnShift") and not IsShiftKeyDown() then
    return false
  end
  if Database:GetValue("isShowOnControl") and not IsControlKeyDown() then
    return false
  end
  if Database:GetValue("isShowOnAlt") and not IsAltKeyDown() then
    return false
  end
  -- this will only be able to be true on Mac clients
  if Database:GetValue("isShowOnMeta") and not IsMetaKeyDown() then
    return false
  end
  return true
end

--- Generates a formatted tooltip line from a version lookup result
-- @param lookup The result from API.GetItemVersion(). Must be non-nil.
-- function TooltipMixin:GenerateLine(lookup)
--   local expacShort = lookup.expac.shortName
--   local expacLong = lookup.expac.canonName
--   local versionShort = format("%d.%d.%d", lookup.expac.major, lookup.minor, lookup.patch)
--   local versionLong = format("%d.%d.%d.%d", lookup.expac.major, lookup.minor, lookup.patch, lookup.build)

--   return self.db.profile.tooltipStringFormat
--       :gsub("{expacShort}", expacShort)
--       :gsub("{expacLong}", expacLong)
--       :gsub("{versionLong}", versionLong)
--       :gsub("{versionShort}", versionShort)
-- end

local function hook(tooltip, data)
  -- GameTooltip is the one attached to the mouse
  -- ItemRefTooltip is the static one after clicking an item link
  if tooltip ~= GameTooltip and tooltip ~= ItemRefTooltip then
    return
  end

  if not areKeyModifiersDown() then
    return
  end

  local itemId
  if data then
    -- mainline way
    itemId = data.id
  else
    -- classic way
    local name, link = tooltip:GetItem()
    if link and name then
      itemId = tonumber(string.match(link, "item:(%d*)"))
    end
  end

  if not itemId then
    return
  end

  local lookup = API.GetItemVersion(itemId, Database:GetValue("applyVersionCorrections"))

  if not lookup then
    return
  end

  local tooltipStringFormat = Database:GetValue("tooltipFormatString")
  local line = API.FormatTooltipString(tooltipStringFormat, lookup)

  tooltip:AddLine(line)
  tooltip:Show()
end

function Private.Tooltip:HookTooltip()
  -- there's two ways to hook the tooltip:
  -- 1. `TooltipDataProcessor.AddTooltipPostCall`. This is newer way and is more
  --    ergonomic at getting tooltip data.
  -- 2. `GameTooltip:HookScript("OnTooltipSetItem", ...)`. This works
  --    everywhere, and requires more manual work to get the item id.

  -- To decide which way, we used to just check for the existence of global
  -- `TooltopDataProcessor`, but that became insufficient when Cata Classic came
  -- out and this global was defined, but `AddTooltipPostCall` wouldn't work.
  -- Therefore, we arbitrarily check if version 10 or higher (i.e. >= 100000 toc
  -- version).
  if TooltipDataProcessor and select(4, GetBuildInfo()) >= 100000 then
    TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item, hook)
  else
    GameTooltip:HookScript("OnTooltipSetItem", hook)
    ItemRefTooltip:HookScript("OnTooltipSetItem", hook)
  end
end
