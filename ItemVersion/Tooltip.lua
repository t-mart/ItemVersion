local addonName, ItemVersion = ...

local L = LibStub("AceLocale-3.0"):GetLocale(addonName)
local API = ItemVersion.API
local Util = ItemVersion.Util

local TooltipMixin = {}

ItemVersion.Tooltip = {}

function ItemVersion.Tooltip:New(db)
  local t = {
    db = db,
  }

  return Util.Mixin(t, TooltipMixin)
end

local WrapTextInColor = function(text, color)
  local hex = ("ff%.2x%.2x%.2x"):format(Round(color.r * 255), Round(color.g * 255), Round(color.b * 255))
  return WrapTextInColorCode(text, hex)
end

function TooltipMixin:ConfiguredModifiersAreDown()
  if self.db.profile.keyModifiers.shift and not IsShiftKeyDown() then
    return false
  end
  if self.db.profile.keyModifiers.control and not IsControlKeyDown() then
    return false
  end
  if self.db.profile.keyModifiers.alt and not IsAltKeyDown() then
    return false
  end
  -- this will only be able to be true on Mac clients
  if self.db.profile.keyModifiers.meta and not IsMetaKeyDown() then
    return false
  end
  return true
end

function TooltipMixin:GenerateLine(version)
  local line = ""

  -- prefix
  if self.db.profile.showPrefix then
    line = line .. WrapTextInColor(L["Added in"], self.db.profile.prefixColor) .. " "
  end

  -- expac
  local expacName
  if version then
    local expac = API:getVersionExpac(version)
    if self.db.profile.shortExpacNames then
      expacName = expac.shortName
    else
      expacName = expac.canonName
    end
  else
    expacName = L["Unknown"]
  end
  line = line .. WrapTextInColor(expacName, self.db.profile.expacColor)

  -- version
  if self.db.profile.showVersion then
    local versionString
    if version then
      versionString = API:buildVersionString(version)
    else
      versionString = L["Unknown"]
    end
    line = line .. WrapTextInColor(" (" .. versionString .. ")", self.db.profile.versionColor)
  end

  return line
end

function TooltipMixin:GenerateLineForItemId(itemId)
  local version = API:getItemVersion(itemId, self.db.profile.includeCommunityUpdates)
  return self:GenerateLine(version)
end

function TooltipMixin:GetOnTooltipSetItemFn()
  return function(tooltip, data)
    -- GameTooltip is the one attached to the mouse
    -- ItemRefTooltip is the static one after clicking an item link
    if tooltip ~= GameTooltip and tooltip ~= ItemRefTooltip then
      return
    end

    if not self:ConfiguredModifiersAreDown() then
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

    local version = API:getItemVersion(itemId, self.db.profile.includeCommunityUpdates)

    if not version and not self.db.profile.showWhenMissing then
      return
    end

    local line = self:GenerateLine(version)

    tooltip:AddLine(line)
    tooltip:Show()
  end
end

function TooltipMixin:HookTooltipCall()
  if TooltipDataProcessor then
    TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item, self:GetOnTooltipSetItemFn())
  else
    GameTooltip:HookScript("OnTooltipSetItem", self:GetOnTooltipSetItemFn())
    ItemRefTooltip:HookScript("OnTooltipSetItem", self:GetOnTooltipSetItemFn())
  end
end
