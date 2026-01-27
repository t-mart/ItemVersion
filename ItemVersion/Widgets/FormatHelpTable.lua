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

-- TODO: instead of hardcode, use the example itemID for each expansion and choose one randomly
-- TODO: instead of hardcoding example output, generate it
local DATA = {
    { L["Token"],        L["Description"],                     L["Example"] }, -- Header
    { "{expacLong}",     L["Canonical name of the expansion"], L["Mists of Pandaria"] },
    { "{expacShort}",    L["Short name of the expansion"],     L["MoP"] },
    { "{expacIcon}",     L["Expansion icon"],                  format("|T%s:16:32|t", Private.Expansion.ALL[5].texture) },
    { "{versionFull}",   L["Full version"],                    "5.2.5.23457" },
    { "{versionTriple}", L["Major, minor, and patch version"], "5.2.5" },
    { "{buildNumber}",   L["Build number only"],               "23457" },
}

--[[-----------------------------------------------------------------------------
Methods
-------------------------------------------------------------------------------]]
local methods = {
    ["OnAcquire"] = function(self, ...)
        -- TODO: does this need to be here, or could we do in constructor?
        self:SetWidth(LEFT_PADDING + LEFT_COL_WIDTH + COL_GAP + 200 + LEFT_PADDING) -- Width with padding
        self:SetHeight(#DATA * ROW_HEIGHT)                                          -- Height for all rows
    end,

    ["OnRelease"] = function(self, ...) end,

    ["SetText"] = function(self, ...) end,

    ["SetFontObject"] = function(self, ...) end,

    ["SetData"] = function(self, ...) end,
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

    -- Create FontStrings for each row
    -- local labels = {}
    for i, row in ipairs(DATA) do
        local leftLabel = frame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
        leftLabel:SetPoint("TOPLEFT", frame, "TOPLEFT", LEFT_PADDING, -(i - 1) * ROW_HEIGHT)
        if i == 1 then
            leftLabel:SetFont("GameFontNormal", fontSize + 2, "OUTLINE")
            leftLabel:SetTextColor(1.0, 0.82, 0.0)
        else
            leftLabel:SetFont(fontPath, fontSize, fontFlags)
            leftLabel:SetTextColor(1, 1, 1)
        end
        leftLabel:SetText(row[1])

        -- middle column is description
        local middleLabel = frame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
        middleLabel:SetPoint("TOPLEFT", frame, "TOPLEFT", LEFT_PADDING + LEFT_COL_WIDTH + COL_GAP, -(i - 1) * ROW_HEIGHT)
        if i == 1 then
            middleLabel:SetFont("GameFontNormal", fontSize + 2, "OUTLINE")
            middleLabel:SetTextColor(1.0, 0.82, 0.0)
        else
            middleLabel:SetTextColor(0.9, 0.9, 0.9)
        end
        middleLabel:SetText(row[2])

        -- right column is example output
        local rightLabel = frame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
        rightLabel:SetPoint("TOPLEFT", frame, "TOPLEFT", LEFT_PADDING + LEFT_COL_WIDTH + COL_GAP + 300,
            -(i - 1) * ROW_HEIGHT)
        if i == 1 then
            rightLabel:SetFont("GameFontNormal", fontSize + 2, "OUTLINE")
            rightLabel:SetTextColor(1.0, 0.82, 0.0)
        else
            rightLabel:SetFont(fontPath, fontSize, fontFlags)
            rightLabel:SetTextColor(0.6, 0.8, 1.0)
        end
        rightLabel:SetText(row[3])

        -- Store references
        -- labels[i] = { left = leftLabel, right = rightLabel }
    end

    -- Create widget
    local widget = {
        -- labels = labels,
        frame = frame,
        type = Type
    }
    for method, func in pairs(methods) do
        widget[method] = func
    end

    return AceGUI:RegisterAsWidget(widget)
end

AceGUI:RegisterWidgetType(Type, Constructor, Version)
