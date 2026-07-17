local AceGUI = LibStub("AceGUI-3.0")

local Type = "ItemVersion-PreviewIcon"
local Version = 1

local methods = {
  ["OnAcquire"] = function() end,

  ["OnRelease"] = function() end,

  -- AceConfigDialog forwards the option's `arg` here, which is how a
  -- dialogControl receives data of its own.
  ["SetCustomData"] = function(self, itemId)
    self.icon:SetTexture(C_Item.GetItemIconByID(itemId))

    self.frame:SetScript("OnEnter", function(frame)
      GameTooltip:SetOwner(frame, "ANCHOR_RIGHT")
      GameTooltip:SetItemByID(itemId)
      GameTooltip:Show()
    end)

    self.frame:SetScript("OnLeave", function()
      GameTooltip:Hide()
    end)
  end,

  -- AceConfigDialog drives a "description" option as if it were a Label. The
  -- icon comes from SetCustomData, so there is nothing for these to do.
  ["SetText"] = function() end,

  ["SetFontObject"] = function() end,
}

local function Constructor()
  local frame = CreateFrame("Frame", nil, UIParent)
  frame:Hide()

  frame:SetSize(32, 40)
  local icon = frame:CreateTexture(nil, "ARTWORK")
  icon:SetAllPoints(frame)

  -- Create widget
  local widget = {
    frame = frame,
    icon = icon,
    type = Type,
  }

  for methodName, methodFunc in pairs(methods) do
    widget[methodName] = methodFunc
  end

  return AceGUI:RegisterAsWidget(widget)
end

AceGUI:RegisterWidgetType(Type, Constructor, Version)
