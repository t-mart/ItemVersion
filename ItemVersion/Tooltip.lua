local addonName, ItemVersion = ...

local L = LibStub("AceLocale-3.0"):GetLocale(addonName)

function ItemVersion:ConfiguredModifiersAreDown()
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

function ItemVersion:TooltipLine(version)
  local line = ""

  -- prefix
  if self.db.profile.showPrefix then
    line = line .. self.Util.WrapTextInColor(L["Added in"], self.db.profile.prefixColor) .. " "
  end

  -- expac
  local expacName
  if version then
    local expac = self:getVersionExpac(version)
    if self.db.profile.shortExpacNames then
      expacName = L[expac.shortName]
    else
      expacName = L[expac.canonName]
    end
  else
    expacName = L["Unknown"]
  end
  line = line .. self.Util.WrapTextInColor(expacName, self.db.profile.expacColor)

  -- version
  if self.db.profile.showVersion then
    local versionString
    if version then
      versionString = self:buildVersionString(version)
    else
      versionString = L["Unknown"]
    end
    line = line ..
        self.Util.WrapTextInColor(" (" .. versionString .. ")", self.db.profile.versionColor)
  end

  return line
end

function ItemVersion:TooltipLineForItemId(itemId)
  local version = self:getItemVersion(itemId)
  return self:TooltipLine(version)
end

function ItemVersion:OnTooltipSetItem(tooltip, data)
  if (tooltip ~= GameTooltip and tooltip ~= ItemRefTooltip) then
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
    local name, link = GameTooltip:GetItem() -- will this break if its ItemRefTooltip?
    if (link) and (name) then
      itemId = tonumber(string.match(link, "item:(%d*)"))
    end
  end

  if not itemId then
    return
  end

  local version = self:getItemVersion(itemId)

  if not version and not self.db.profile.showWhenMissing then
    return
  end

  local tooltipLine = self:TooltipLine(version)

  tooltip:AddLine(tooltipLine)
  tooltip:Show()
end

function ItemVersion:HookTooltipCall()
  if TooltipDataProcessor then
    TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item,
                                            function(...) self:OnTooltipSetItem(...) end)
  else
    GameTooltip:HookScript("OnTooltipSetItem", function(...) self:OnTooltipSetItem(...) end)
  end
end
