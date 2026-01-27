local _, Private = ...

local AceGUI = LibStub("AceGUI-3.0")

local Type = "ItemVersion-PreviewIcon"
local Version = 1

local methods = {
    ["OnAcquire"] = function()
    end,

    ["OnRelease"] = function() end,

    ["SetText"] = function(self, text)
        -- use the hack: this is the way to get a stringified expansion major version
        -- we use this to look up the expansion and render its icon
        local expansionMajor = tonumber(text)
        local expansion = Private.Expansion:GetExpansionFromMajor(expansionMajor)
        local itemId = expansion.previewItemId
        self.icon:SetTexture(C_Item.GetItemIconByID(itemId))

        self.frame:SetScript("OnEnter", function(s)
            GameTooltip:SetOwner(s, "ANCHOR_RIGHT")
            GameTooltip:SetItemByID(itemId)
            GameTooltip:Show()
        end)

        self.frame:SetScript("OnLeave", function()
            GameTooltip:Hide()
        end)
    end,

    ["SetFontObject"] = function() end,
}


local function Constructor()
    local frame = CreateFrame("Frame", nil, UIParent)
    frame:Hide()

    frame:SetSize(32, 40)
    local icon = frame:CreateTexture(nil, "ARTWORK")
    icon:SetAllPoints(frame)
    icon:SetTexture(C_Item.GetItemIconByID(124103))

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
