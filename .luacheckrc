-- "Only a subset of version 5.1 of the official Lua specification is implemented"
-- https://wow.gamepedia.com/Lua
std = "lua51"

-- Data.lua is where our refreshed data comes in.
-- It's built dynamically, so we don't have too much control over it.
-- The current check failures seem innocent enough too.
files["ItemVersion/Data.lua"] = {
	ignore = {
		"631", -- Line is too long.
		"211" -- Unused local variable.
	}
}

globals = {
	"format",  -- provided by WoW
	"strmatch",  -- provided by WoW
	"C_Timer",  -- provided by WoW
	"GameTooltip",  -- provided by WoW
	"ItemVersion"  -- provided by us.
}
