local addonName, AddonTable = ...

ItemVersion = LibStub("AceAddon-3.0"):GetAddon(addonName)
local L = LibStub("AceLocale-3.0"):GetLocale(addonName)

local function CreateColorNoAlpha(c)
  return CreateColor(c.r, c.g, c.b, 1.0)
end

function ItemVersion:tooltipLine(itemId)
  local version = self:getItemVersion(itemId)

  if not version and not self.db.profile.showWhenMissing then
    return
  end

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
      expacName = expac.shortName
    else
      expacName = expac.canonName
    end
  else
    expacName = "unknown"
  end
  local expacColor = CreateColorNoAlpha(self.db.profile.expacColor)
  line = line .. WrapTextInColor(L[expacName], expacColor)

  -- version
  if self.db.profile.showVersion then
    local versionString
    if version then
      versionString = self:buildVersionString(version)
    else
      versionString = L["unknown"]
    end
    local versionColor = CreateColorNoAlpha(self.db.profile.versionColor)
    line = line ..  WrapTextInColor(" (" .. versionString .. ")", versionColor)
  end

  return line
end

function ItemVersion:OnTooltipSetItem(tooltip, data)
  if (tooltip ~= GameTooltip and tooltip ~= ItemRefTooltip) then
      return
  end

  local itemId = data.id

  if not itemId then
    return
  end

  tooltip:AddLine(self:tooltipLine(itemId))
  tooltip:Show()
end
