local addonName, ItemVersion = ...

local L = LibStub("AceLocale-3.0"):GetLocale(addonName)

-- Show with modifier keys:
-- - Show always
-- - Show with Shift
-- - Show with Ctrl
-- - Show with Alt
-- - Show with Shift + Ctrl
-- - Show with Shift + Alt
-- - Show with Ctrl + Alt
-- - Show with Shift + Ctrl + Alt

-- Show preview


local function CreateColorNoAlpha(c)
  return CreateColor(c.r, c.g, c.b, 1.0)
end

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
  return true
end

function ItemVersion:TooltipLine(version)
  local line = ""

  -- prefix
  if self.db.profile.showPrefix then
    local prefixColor = CreateColorNoAlpha(self.db.profile.prefixColor)
    line = line .. WrapTextInColor(L["Added in"], prefixColor) .. " "
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
  local expacColor = CreateColorNoAlpha(self.db.profile.expacColor)
  line = line .. WrapTextInColor(expacName, expacColor)

  -- version
  if self.db.profile.showVersion then
    local versionString
    if version then
      versionString = self:buildVersionString(version)
    else
      versionString = L["Unknown"]
    end
    local versionColor = CreateColorNoAlpha(self.db.profile.versionColor)
    line = line .. WrapTextInColor(" (" .. versionString .. ")", versionColor)
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

  local itemId = data.id

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
