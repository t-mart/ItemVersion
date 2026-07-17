local AddonName, Private = ...

local AceGUI = LibStub("AceGUI-3.0")
local LSM = LibStub("LibSharedMedia-3.0")

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)

local Type = "ItemVersion-FormatHelpTable"
local Version = 1

local ROW_HEIGHT = 18
local COL_GAP = 10
local HEADER_SIZE_BUMP = 2
local HEADER_COLOR = { r = 1.0, g = 0.82, b = 0.0 }
local BODY_COLOR = { r = 0.9, g = 0.9, b = 0.9 }
local TOKEN_COLOR = { r = 1, g = 1, b = 1 }
local MONO_FONT = "JetBrains Mono NL"

-- Any item in the database will do. This one lands on 3.3.0, so every token has
-- something to show.
local EXAMPLE_ITEM_ID = 50818

---@class FormatHelpColumn
---@field header string Column heading
---@field width number Space the column occupies before the next one starts
---@field mono boolean Whether body cells use the monospace font
---@field bodyColor Color Body cell text color
---@field anchor string Which point of the cell sits at the column offset
---@field cell fun(tokenInfo: TokenInfo, lookup: ItemVersionLookup): string

---@type FormatHelpColumn[]
local COLUMNS = {
  {
    header = L["Token"],
    width = 140,
    mono = true,
    bodyColor = TOKEN_COLOR,
    anchor = "TOPLEFT",
    cell = function(tokenInfo)
      return tokenInfo.string
    end,
  },
  {
    header = L["Description"],
    width = 290,
    mono = false,
    bodyColor = BODY_COLOR,
    anchor = "TOPLEFT",
    cell = function(tokenInfo)
      return tokenInfo.description
    end,
  },
  {
    header = L["Example"],
    width = 200,
    mono = true,
    bodyColor = BODY_COLOR,
    -- TOP rather than TOPLEFT, so this column centers on its offset instead of
    -- starting there. Carried over from the layout this file used to hardcode.
    anchor = "TOP",
    cell = function(tokenInfo, lookup)
      return lookup:Format(tokenInfo.string)
    end,
  },
}

---Horizontal offset of each column, and the width they span in total
---@param columns FormatHelpColumn[]
---@return number[] offsets
---@return number totalWidth
local function measureColumns(columns)
  local offsets = {}
  local x = 0

  for i, column in ipairs(columns) do
    offsets[i] = x
    x = x + column.width + COL_GAP
  end

  return offsets, x - COL_GAP
end

local COLUMN_X, TABLE_WIDTH = measureColumns(COLUMNS)

---Build the table contents, header first
---@param lookup ItemVersionLookup The example item's version, for the example column
---@return string[][] rows
local function buildRows(lookup)
  local header = {}
  for i, column in ipairs(COLUMNS) do
    header[i] = column.header
  end

  local rows = { header }

  for _, tokenInfo in ipairs(Private.Tokens) do
    local row = {}
    for i, column in ipairs(COLUMNS) do
      row[i] = column.cell(tokenInfo, lookup)
    end
    table.insert(rows, row)
  end

  return rows
end

---@class FormatHelpFonts
---@field gameFile string Font file backing GameFontNormal
---@field monoPath string Font file for the monospace columns
---@field size number
---@field flags string

---Draw one cell
---@param frame table The widget frame
---@param column FormatHelpColumn
---@param x number Horizontal offset of the column
---@param y number Vertical offset of the row
---@param text string
---@param isHeader boolean
---@param fonts FormatHelpFonts
local function drawCell(frame, column, x, y, text, isHeader, fonts)
  local label = frame:CreateFontString(nil, "ARTWORK", "GameFontNormal")
  label:SetPoint(column.anchor, frame, "TOPLEFT", x, y)

  if isHeader then
    label:SetFont(fonts.gameFile, fonts.size + HEADER_SIZE_BUMP, "OUTLINE")
    label:SetTextColor(HEADER_COLOR.r, HEADER_COLOR.g, HEADER_COLOR.b)
  else
    -- Columns without a font of their own keep the GameFontNormal template
    -- they were created with.
    if column.mono then
      label:SetFont(fonts.monoPath, fonts.size, fonts.flags)
    end
    label:SetTextColor(column.bodyColor.r, column.bodyColor.g, column.bodyColor.b)
  end

  label:SetText(text)
end

--[[-----------------------------------------------------------------------------
Methods
-------------------------------------------------------------------------------]]
local methods = {
  -- AceGUI clears the frame's size on release, so it is set here rather than in
  -- the constructor.
  ["OnAcquire"] = function(self)
    self:SetWidth(TABLE_WIDTH)
    self:SetHeight((#Private.Tokens + 1) * ROW_HEIGHT)
  end,

  -- AceConfigDialog drives a "description" option as if it were a Label. The
  -- table draws itself, so there is nothing for these to do.
  ["SetText"] = function() end,

  ["SetFontObject"] = function() end,
}

--[[-----------------------------------------------------------------------------
Constructor
-------------------------------------------------------------------------------]]
local function Constructor()
  local frame = CreateFrame("Frame", nil, UIParent)
  frame:Hide()

  local gameFile, size, flags = GameFontNormal:GetFont()
  local fonts = {
    gameFile = gameFile,
    monoPath = LSM:Fetch("font", MONO_FONT),
    size = size,
    flags = flags,
  }

  local lookup = Private.API.GetItemVersion(EXAMPLE_ITEM_ID, true)

  for rowIndex, row in ipairs(buildRows(lookup)) do
    local y = -(rowIndex - 1) * ROW_HEIGHT
    for colIndex, column in ipairs(COLUMNS) do
      drawCell(frame, column, COLUMN_X[colIndex], y, row[colIndex], rowIndex == 1, fonts)
    end
  end

  local widget = {
    frame = frame,
    type = Type,
  }
  for method, func in pairs(methods) do
    widget[method] = func
  end

  return AceGUI:RegisterAsWidget(widget)
end

AceGUI:RegisterWidgetType(Type, Constructor, Version)
