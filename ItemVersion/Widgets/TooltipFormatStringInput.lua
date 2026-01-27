local AceGUI = LibStub("AceGUI-3.0")
local LSM = LibStub("LibSharedMedia-3.0")

local Type = "ItemVersion-TooltipFormatStringInput"
local Version = 1


local methods = {
    ["OnAcquire"] = function(self, ...)
        self.descLabel:OnAcquire(...)
        self.editbox:OnAcquire(...)
    end,

    ["OnRelease"] = function(self)
        -- Clean up if needed
    end,

    ["OnWidthSet"] = function(self, width)
    end,

    ["SetText"] = function(self, text)
        -- Set the text of the input box
        self.editbox:SetText(text)
    end,

    ["GetText"] = function(self)
        -- Get the text of the input box
        return self.editbox:GetText()
    end,

    ["SetLabel"] = function(self, label)
        -- Set the label of the input box
        self.editbox:SetLabel(label)
    end,

    ["SetScript"] = function(self, scriptName, func)
        -- Set scripts like OnEnterPressed, OnTextChanged, etc.
        DevTool:AddData(self, "self")
        self.editbox.editbox:SetScript(scriptName, func)
    end,
}

local function Constructor()
	local frame = CreateFrame("Frame", nil, UIParent)
	frame:Hide()

    -- Track the current Y offset for positioning children
    local yOffset = 0
    local padding = 10  -- Padding between widgets

    

    -- Create widget
    local widget = {
        frame = frame,
        descLabel = descLabel,
        editbox = editbox,
        type = Type,
    }

    -- Add methods
    for methodName, methodFunc in pairs(methods) do
        widget[methodName] = methodFunc
    end

    return AceGUI:RegisterAsWidget(widget)
end

AceGUI:RegisterWidgetType(Type, Constructor, Version)
