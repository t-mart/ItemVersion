local _, Private = ...

---@class Color
---@field r number Red component (0.0 to 1.0)
---@field g number Green component (0.0 to 1.0)
---@field b number Blue component (0.0 to 1.0)
---@field a number|nil Alpha component (0.0 to 1.0), defaults to 1.0

Private.Color = {}
local Color = Private.Color

---Returns a white color
---@return Color
function Color.White()
    return { r = 1.0, g = 1.0, b = 1.0 }
end

---Returns a blue color
---@return Color
function Color.Blue()
    return { r = 0.31, g = 0.63, b = 1.0 }
end

---Converts a color to a hex string for WoW color codes
---@param color Color The color to convert
---@return string hex The hex string in format "AARRGGBB"
function Color.ToHexString(color)
    local r = math.floor(color.r * 255)
    local g = math.floor(color.g * 255)
    local b = math.floor(color.b * 255)
    local a = math.floor((color.a or 1.0) * 255)
    return format("%02X%02X%02X%02X", a, r, g, b)
end

---Wraps text with WoW color codes
---@param text string The text to wrap
---@param color Color The color to use
---@return string wrapped The text wrapped with color codes
function Color.WrapTextWithColor(text, color)
    local hex = Color.ToHexString(color)
    return format("|c%s%s|r", hex, text)
end