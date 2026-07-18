local AceGUI = LibStub("AceGUI-3.0")

local Type = "ItemVersion-AutoWidthButton"
local Version = 1

-- A native AceGUI button sized to its own label rather than the fixed width
-- AceConfigDialog hands every control. Auto width tracks the text, so the button
-- stays snug in any locale instead of padding out to a fixed box.
local function Constructor()
  local button = AceGUI:Create("Button")

  local baseSetWidth = button.SetWidth
  button:SetAutoWidth(true)

  -- AceConfigDialog calls SetWidth after creation to impose its column width,
  -- which would undo the auto width. Redirect it back to fitting the text. Uses
  -- the captured base method, since SetAutoWidth itself calls SetWidth.
  button.SetWidth = function(self)
    baseSetWidth(self, self.text:GetStringWidth() + 30)
  end

  return button
end

AceGUI:RegisterWidgetType(Type, Constructor, Version)
