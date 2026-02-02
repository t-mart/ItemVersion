-- this is a mess. i need help fixing this file up.
local AddonName, Private = ...

local AceGUI = LibStub("AceGUI-3.0")
local LSM = LibStub("LibSharedMedia-3.0")

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)

local Type = "ItemVersion-FormatHelpTable"
local Version = 1

local ROW_HEIGHT = 18
local COL_GAP = 10
local LEFT_COL_WIDTH = 140
local LEFT_PADDING = 0

local EXAMPLE_ITEM_ID = 50818

local labels = {
    { L["Token"], L["Description"], }, -- Header
}
for _, tokenInfo in ipairs(Private.Tokens) do
    table.insert(labels, { tokenInfo.string, tokenInfo.description })
end

--[[-----------------------------------------------------------------------------
Methods
-------------------------------------------------------------------------------]]
local methods = {
    ["OnAcquire"] = function(self)
        -- TODO: does this need to be here, or could we do in constructor?
        self:SetWidth(LEFT_PADDING + LEFT_COL_WIDTH + COL_GAP + 200 + LEFT_PADDING) -- Width with padding
        self:SetHeight(#labels * ROW_HEIGHT)                                        -- Height for all rows
    end,

    ["OnRelease"] = function() end,

    ["SetText"] = function() end,

    ["SetFontObject"] = function() end,

    ["SetData"] = function() end,
}

--[[-----------------------------------------------------------------------------
Constructor
-------------------------------------------------------------------------------]]
local function Constructor()
    local frame = CreateFrame("Frame", nil, UIParent)
    frame:Hide()

    -- Get JetBrains Mono font
    local fontPath = LSM:Fetch("font", "JetBrains Mono NL")
    local _, fontSize, fontFlags = GameFontNormal:GetFont()

    -- lookup the hearthstone
    local lookup = Private.API.GetItemVersion(EXAMPLE_ITEM_ID, true)

    -- Create FontStrings for each row
    for i, row in ipairs(labels) do
        local token, description = row[1], row[2]
        local example = lookup:Format(token)
        local leftLabel = frame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
        leftLabel:SetPoint("TOPLEFT", frame, "TOPLEFT", LEFT_PADDING, -(i - 1) * ROW_HEIGHT)
        if i == 1 then
            leftLabel:SetFont("GameFontNormal", fontSize + 2, "OUTLINE")
            leftLabel:SetTextColor(1.0, 0.82, 0.0)
        else
            leftLabel:SetFont(fontPath, fontSize, fontFlags)
            leftLabel:SetTextColor(1, 1, 1)
        end
        leftLabel:SetText(token)

        -- middle column is description
        local middleLabel = frame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
        middleLabel:SetPoint("TOPLEFT", frame, "TOPLEFT", LEFT_PADDING + LEFT_COL_WIDTH + COL_GAP, -(i - 1) * ROW_HEIGHT)
        if i == 1 then
            middleLabel:SetFont("GameFontNormal", fontSize + 2, "OUTLINE")
            middleLabel:SetTextColor(1.0, 0.82, 0.0)
        else
            middleLabel:SetTextColor(0.9, 0.9, 0.9)
        end
        middleLabel:SetText(description)

        -- right column is example output
        local rightLabel = frame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
        rightLabel:SetPoint("TOP", frame, "TOPLEFT", LEFT_PADDING + LEFT_COL_WIDTH + COL_GAP + 300,
            -(i - 1) * ROW_HEIGHT)
        if i == 1 then
            rightLabel:SetFont("GameFontNormal", fontSize + 2, "OUTLINE")
            rightLabel:SetTextColor(1.0, 0.82, 0.0)
            rightLabel:SetText(L["Example"])
        else
            rightLabel:SetFont(fontPath, fontSize, fontFlags)
            rightLabel:SetTextColor(0.9, 0.9, 0.9)
            rightLabel:SetText(example)
        end
    end

    -- Create widget
    local widget = {
        frame = frame,
        type = Type
    }
    for method, func in pairs(methods) do
        widget[method] = func
    end

    return AceGUI:RegisterAsWidget(widget)
end

AceGUI:RegisterWidgetType(Type, Constructor, Version)
