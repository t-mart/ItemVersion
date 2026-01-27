local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)
local AceConfig = LibStub("AceConfig-3.0")
local AceConfigDialog = LibStub("AceConfigDialog-3.0")

Private.Options = {
  OPTIONS_APP_NAME = AddonName .. "Options",
  PROFILE_OPTIONS_APP_NAME = AddonName .. "ProfileOptions",
}
local Options = Private.Options

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
  if expansion:IsActive() then
    previewWidgets[format("preview-%d", expansion.major)] = {
      order = expansion.major,
      type = "description",
      width = 0.25,
      name = tostring(expansion.major), -- HACK: a way to provide data to the widget
      dialogControl = "ItemVersion-PreviewIcon",
    }
  end
end

local OPTIONS_TABLE = {
  name = AddonName,
  handler = AccessHandler,
  type = "group",
  args = {
    lineColor = {
      type = "color",
      name = L["Line Color"],
      desc = L["Color of the line of text in the tooltip"],
      get = "GetColor",
      set = "SetColor",
      arg = "lineColor",
      order = 1,
    },
    keyModifierGroup = {
      type = "group",
      name = L["Key Modifiers Needed to Show Info"],
      inline = true,
      order = 3,
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
          hidden = function() return not IsMacClient() end,
          get = "GetValue",
          set = "SetValue",
          arg = "showOnMeta",
          order = 4,
        },
      }
    },
    applyVersionCorrections = {
      type  = "toggle",
      name  = L["Apply version corrections"],
      desc  = L["Correct the version for some items whose release version is different than their usable version."],
      get   = "GetValue",
      set   = "SetValue",
      arg   = "applyVersionCorrections",
      width = "full",
      order = 4,
    },
    tooltipFormatGroup = {
      type = "group",
      name = L["Tooltip format"],
      inline = true,
      order = 5,
      args = {
        intro = {
          type = "description",
          name = L["Customize the format of the item version information shown in tooltips."],
          fontSize = "medium",
          order = 1,
        },
        tooltipFormat = {
          type = "input",
          name = L["Tooltip format"],
          desc = L["Provide a template to format the tooltip line"],
          get = "GetValue",
          set = "SetValue",
          arg = "tooltipFormat",
          width = "full",
          order = 2,
          dialogControl = "ItemVersion-MonoEditBox",
        },
        tooltipFormatStringHelp = {
          type = "group",
          name = L["Format Tokens"],
          inline = true,
          order = 3,
          args = {
            formatHelp = {
              order = 1,
              type = "description",
              name = "", -- Ignored by our widget, but required by AceConfig
              dialogControl = "ItemVersion-FormatHelpTable",
            },
          },
        },
      }
    },
    preview = {
      type = "group",
      name = L["Mouseover Preview"],
      inline = true,
      order = 6,
      args = previewWidgets,
    }
  },
}

---Register the main options panel
local function registerMainOptions()
  AceConfig:RegisterOptionsTable(Options.OPTIONS_APP_NAME, OPTIONS_TABLE)
  AceConfigDialog:AddToBlizOptions(Options.OPTIONS_APP_NAME, AddonName)
end

---Register the profile management options panel
local function registerProfileOptions()
  local profiles = Private.DatabaseManager:GetProfileOptionsTable()
  AceConfig:RegisterOptionsTable(Options.PROFILE_OPTIONS_APP_NAME, profiles)
  AceConfigDialog:AddToBlizOptions(Options.PROFILE_OPTIONS_APP_NAME, L["Profiles"], AddonName)
end

---Register all options panels with the game's interface options
function Options.Register()
  registerMainOptions()
  registerProfileOptions()
end
