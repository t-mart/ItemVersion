local AceGUI = LibStub("AceGUI-3.0")
local LSM = LibStub("LibSharedMedia-3.0")

local Type = "ItemVersion-MonoEditBox"
local Version = 1

local function Constructor()
	local editbox = AceGUI:Create("EditBox")

	local fontPath = LSM:Fetch("font", "JetBrains Mono NL")
	local _, size, flags = GameFontNormal:GetFont()
	editbox.editbox:SetFont(fontPath, size, flags)

	return AceGUI:RegisterAsWidget(editbox)
end

AceGUI:RegisterWidgetType(Type, Constructor, Version)
