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

-- Different languages shouldn't have code formatting requirements
files['ItemVersion/Locales/*.lua'] = {
	ignore = {
		"631", -- Line is too long.
	}
}

globals = {
	-- provided by WoW API
	-- "format",
	-- "strmatch",
	-- "C_Timer",
	"GameTooltip",
	"GetAddOnMetadata",
	"SlashCmdList",
	"EXPANSION_NAME0",
	"EXPANSION_NAME1",
	"EXPANSION_NAME2",
	"EXPANSION_NAME3",
	"EXPANSION_NAME4",
	"EXPANSION_NAME5",
	"EXPANSION_NAME6",
	"EXPANSION_NAME7",
	"EXPANSION_NAME8",
	"GAME_VERSION_LABEL",
	"EXPANSION_FILTER_TEXT",
	"UNKNOWN",
	"ItemRefTooltip",
	"TooltipDataProcessor",
	"Enum",
	"RegisterNewSlashCommand",
	"EXPANSION_NAME9",
	"PREVIEW",
	"SHIFT_KEY_TEXT",
	"ALT_KEY_TEXT",
	"CTRL_KEY_TEXT",
	"MODE",
	"SafePack",
	"TableUtil",
	"Settings",
	"CreateColor",
	"IsShiftKeyDown",
	"IsControlKeyDown",
	"IsAltKeyDown",
	"WrapTextInColor",
	"IsMacClient",
	"IsMetaKeyDown",
	"CMD_KEY_TEXT",
	"InterfaceOptionsFrame_OpenToCategory",
	"Round",
	"WrapTextInColorCode",

	-- provided by libs
	"LibStub",

	-- provided by ItemVersion
	"ItemVersion",
}
