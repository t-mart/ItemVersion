local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)
local AceConfig = LibStub("AceConfig-3.0")
local AceConfigDialog = LibStub("AceConfigDialog-3.0")

Private.Options = {
  OPTIONS_APP_NAME = AddonName .. "Options",
  PROFILE_OPTIONS_APP_NAME = AddonName .. "ProfileOptions",
}
local Options = Private.Options

-- Live ItemVersion-MonoEditBox widgets. AceConfigDialog pools and reuses them,
-- so more than one can exist across the panel's lifetime; only the one on screen
-- is visible.
local formatFields = {}

---Register a format-string edit widget as a target for token insertion
---@param widget table The AceGUI EditBox widget wrapping the format field
function Options.RegisterFormatField(widget)
  for _, existing in ipairs(formatFields) do
    if existing == widget then
      return
    end
  end

  formatFields[#formatFields + 1] = widget
end

---The format-field widget currently on screen, if any
---@return table|nil widget
local function visibleFormatWidget()
  for _, widget in ipairs(formatFields) do
    local frame = widget.editbox
    if frame and frame:IsVisible() then
      return widget
    end
  end
end

---Append a token to the format string and save it
---
---Commits straight to the profile rather than only to the edit box. The Add
---control is an AceConfig execute, which refreshes the whole options panel on
---click; that refresh re-reads the field from the saved value, so an edit only
---to the box would be discarded. Appending to the saved value and mirroring it
---into the visible widget keeps both in step, whether or not a refresh follows.
---@param text string The token to append, such as "{expacFull}"
function Options.InsertToken(text)
  local widget = visibleFormatWidget()
  local current = widget and widget:GetText() or Private.Database.profile.tooltipFormat
  local newValue = current .. text

  Private.Database.profile.tooltipFormat = newValue

  if widget then
    widget:SetText(newValue)
  end
end

local AccessHandler = {
  GetValue = function(_, info)
    local key = info.arg
    return Private.Database.profile[key]
  end,
  SetValue = function(_, info, value)
    local key = info.arg
    Private.Database.profile[key] = value
  end,
  GetColor = function(self, info)
    local color = self:GetValue(info)
    return color.r, color.g, color.b
  end,
  SetColor = function(self, info, r, g, b)
    local color = { r = r, g = g, b = b }
    self:SetValue(info, color)
  end,
}

local previewWidgets = {}
for _, expansion in ipairs(Private.Expansion.All) do
  if expansion:IsPresent() then
    previewWidgets[format("preview-%d", expansion.major)] = {
      order = expansion.major,
      type = "description",
      width = 0.25,
      name = "", -- Ignored by our widget, but required by AceConfig
      arg = expansion.previewItemId,
      dialogControl = "ItemVersion-PreviewIcon",
    }
  end
end

-- Any item in the database will do for the example column. This one lands on
-- 3.3.0, so every token has something to show.
local EXAMPLE_ITEM_ID = 32837

local HEADER_COLOR = "ffffd100" -- gold, the game's usual option-header color
local TOKEN_COLOR = "ffffffff"

-- Relative column widths, as fractions of the token-help row. They sum to under
-- 1 so the four controls share one row, with slack for the layout's spacing.
-- A value too long for its column wraps within it rather than overflowing.
local REL_TOKEN = 0.22
local REL_DESC = 0.40
local REL_EXAMPLE = 0.20
local REL_GAP = 0.04 -- empty spacer between the example and the Add button
local REL_ADD = 0.10

---Wrap text in a WoW color code
---@param hex string An "AARRGGBB" hex string
---@param text string
---@return string
local function colored(hex, text)
  return format("|c%s%s|r", hex, text)
end

---The example rendering of a token. Deferred behind a function so it runs when
---the panel opens, by which point ItemData and the API have loaded (they follow
---this file in the TOC).
---@param tokenInfo TokenInfo
---@return string
local function tokenExample(tokenInfo)
  local lookup = Private.API.GetItemVersion(EXAMPLE_ITEM_ID, true)
  if not lookup then
    return ""
  end

  return lookup:Format(tokenInfo.string)
end

---Build the AceConfig args for the token help: a header row, then one row per
---token of token / description / example / an Add button. Laid out in relative
---widths so the columns track the panel width rather than hardcoded pixels.
---@return table
local function buildTokenHelpArgs()
  local args = {
    headerToken = {
      type = "description",
      order = 1,
      width = "relative",
      relWidth = REL_TOKEN,
      name = colored(HEADER_COLOR, L["Token"]),
    },
    headerDesc = {
      type = "description",
      order = 2,
      width = "relative",
      relWidth = REL_DESC,
      name = colored(HEADER_COLOR, L["Description"]),
    },
    headerExample = {
      type = "description",
      order = 3,
      width = "relative",
      relWidth = REL_EXAMPLE,
      name = colored(HEADER_COLOR, L["Example"]),
    },
    headerAdd = {
      type = "description",
      order = 4,
      width = "relative",
      relWidth = REL_ADD,
      name = " ",
    },
  }

  for i, tokenInfo in ipairs(Private.Tokens) do
    local base = i * 10
    args["token" .. i] = {
      type = "description",
      order = base + 1,
      width = "relative",
      relWidth = REL_TOKEN,
      fontSize = "medium",
      name = colored(TOKEN_COLOR, tokenInfo.string),
    }
    args["desc" .. i] = {
      type = "description",
      order = base + 2,
      width = "relative",
      relWidth = REL_DESC,
      fontSize = "medium",
      name = tokenInfo.description,
    }
    args["example" .. i] = {
      type = "description",
      order = base + 3,
      width = "relative",
      relWidth = REL_EXAMPLE,
      fontSize = "medium",
      name = function()
        return tokenExample(tokenInfo)
      end,
    }
    args["gap" .. i] = {
      type = "description",
      order = base + 4,
      width = "relative",
      relWidth = REL_GAP,
      name = " ",
    }
    args["add" .. i] = {
      type = "execute",
      order = base + 5,
      width = "relative",
      relWidth = REL_ADD,
      name = L["Add"],
      func = function()
        Private.Options.InsertToken(tokenInfo.string)
      end,
    }
  end

  return args
end

local OPTIONS_TABLE = {
  name = AddonName,
  handler = AccessHandler,
  type = "group",
  args = {
    enableTooltip = {
      type = "toggle",
      name = L["Enable tooltip integration"],
      desc = L["Show item version information in tooltips."],
      get = "GetValue",
      set = "SetValue",
      arg = "enableTooltip",
      width = "full",
      order = 0,
    },
    lineColor = {
      type = "color",
      name = L["Tooltip text color"],
      desc = L["Color of the line of text in the tooltip"],
      get = "GetColor",
      set = "SetColor",
      arg = "lineColor",
      order = 1,
      disabled = function()
        return not Private.Database.profile.enableTooltip
      end,
    },
    keyModifierGroup = {
      type = "group",
      name = L["Key Modifiers Needed to Show Info"],
      inline = true,
      order = 3,
      disabled = function()
        return not Private.Database.profile.enableTooltip
      end,
      args = {
        showOnShift = {
          type = "toggle",
          name = SHIFT_KEY_TEXT,
          desc = format(L["Show item version info in tooltips when the %s key is held down."], SHIFT_KEY_TEXT),
          get = "GetValue",
          set = "SetValue",
          arg = "showOnShift",
          order = 1,
        },
        showOnControl = {
          type = "toggle",
          name = CTRL_KEY_TEXT,
          desc = format(L["Show item version info in tooltips when the %s key is held down."], CTRL_KEY_TEXT),
          get = "GetValue",
          set = "SetValue",
          arg = "showOnControl",
          order = 2,
        },
        showOnAlt = {
          type = "toggle",
          name = ALT_KEY_TEXT,
          desc = format(L["Show item version info in tooltips when the %s key is held down."], ALT_KEY_TEXT),
          get = "GetValue",
          set = "SetValue",
          arg = "showOnAlt",
          order = 3,
        },
        showOnMeta = {
          type = "toggle",
          name = CMD_KEY_TEXT,
          desc = format(L["Show item version info in tooltips when the %s key is held down."], CMD_KEY_TEXT),
          hidden = function()
            return not IsMacClient()
          end,
          get = "GetValue",
          set = "SetValue",
          arg = "showOnMeta",
          order = 4,
        },
      },
    },
    applyCorrections = {
      type = "toggle",
      name = L["Apply version corrections"],
      desc = L["Correct the version for some items whose release version is different than their usable version."],
      get = "GetValue",
      set = "SetValue",
      arg = "applyCorrections",
      width = "full",
      order = 4,
      disabled = function()
        return not Private.Database.profile.enableTooltip
      end,
    },
    tooltipFormatGroup = {
      type = "group",
      name = L["Tooltip format"],
      inline = true,
      order = 5,
      disabled = function()
        return not Private.Database.profile.enableTooltip
      end,
      args = {
        intro = {
          type = "description",
          name = L["Customize the format of the item version information shown in tooltips."],
          fontSize = "medium",
          order = 1,
        },
        tooltipFormat = {
          type = "input",
          -- Labelled by the group heading already, so no name of its own. That
          -- also drops the label line above the box, which lets the reset button
          -- share this row rather than aligning to a taller, labelled control.
          name = "",
          desc = L["Provide a template to format the tooltip line"],
          get = "GetValue",
          set = "SetValue",
          arg = "tooltipFormat",
          width = "relative",
          relWidth = 0.8,
          order = 2,
          dialogControl = "ItemVersion-MonoEditBox",
        },
        resetFormat = {
          type = "execute",
          name = L["Reset"],
          desc = L["Reset the tooltip format to its default."],
          order = 3,
          dialogControl = "ItemVersion-AutoWidthButton",
          confirm = true,
          confirmText = L["Reset the tooltip format to its default?"],
          func = function()
            Private.Database.profile.tooltipFormat = Private.Profile.Default("tooltipFormat")
          end,
        },
        tooltipFormatStringHelp = {
          type = "group",
          name = L["Format Tokens"],
          inline = true,
          order = 4,
          args = buildTokenHelpArgs(),
        },
      },
    },
    preview = {
      type = "group",
      name = L["Mouseover Preview"],
      inline = true,
      order = 6,
      args = previewWidgets,
    },
  },
}

---Register the main options panel
local function registerMainOptions()
  AceConfig:RegisterOptionsTable(Options.OPTIONS_APP_NAME, OPTIONS_TABLE)
  AceConfigDialog:AddToBlizOptions(Options.OPTIONS_APP_NAME, AddonName)
end

---Register the profile management options panel
local function registerProfileOptions()
  local profiles = Private.Profile:GetProfileOptionsTable()
  AceConfig:RegisterOptionsTable(Options.PROFILE_OPTIONS_APP_NAME, profiles)
  AceConfigDialog:AddToBlizOptions(Options.PROFILE_OPTIONS_APP_NAME, L["Profiles"], AddonName)
end

---Register all options panels with the game's interface options
function Options.Register()
  registerMainOptions()
  registerProfileOptions()
end
