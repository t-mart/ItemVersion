local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)
local AceConfig = LibStub("AceConfig-3.0")
local AceConfigDialog = LibStub("AceConfigDialog-3.0")

Private.Options = {}

local AccessHandler = {
  GetValue = function(self, info)
    local key = info.arg
    return Private.Database:GetValue(key)
  end,
  SetValue = function(self, info, value)
    local key = info.arg
    Private.Database:SetValue(key, value)
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
for _, expansion in ipairs(Private.Expansion.ALL) do
  previewWidgets[format("preview-%d", expansion.major)] = {
    order = expansion.major,
    type = "description",
    width = 0.25,
    name = tostring(expansion.major), -- HACK: a way to provide data to the widget
    dialogControl = "ItemVersion-PreviewIcon",
  }
end

local OPTIONS_TABLE = {
  name = AddonName,
  handler = AccessHandler,
  type = "group",
  args = {
    tokenColor = {
      type = "color",
      name = L["Token Color"],
      desc = L["Color to use for tokens in tooltips."],
      get = "GetColor",
      set = "SetColor",
      arg = "tokenColor",
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
          arg = "isShowOnShift",
          order = 1,
        },
        showOnControl = {
          type = "toggle",
          name = CTRL_KEY_TEXT,
          desc = format(L["Show item version info in tooltips when the %s key is held down."], CTRL_KEY_TEXT),
          get = "GetValue",
          set = "SetValue",
          arg = "isShowOnControl",
          order = 2,
        },
        showOnAlt = {
          type = "toggle",
          name = ALT_KEY_TEXT,
          desc = format(L["Show item version info in tooltips when the %s key is held down."], ALT_KEY_TEXT),
          get = "GetValue",
          set = "SetValue",
          arg = "isShowOnAlt",
          order = 3,
        },
        showOnMeta = {
          type = "toggle",
          name = CMD_KEY_TEXT,
          desc = format(L["Show item version info in tooltips when the %s key is held down."], CMD_KEY_TEXT),
          hidden = function() return not IsMacClient() end,
          get = "GetValue",
          set = "SetValue",
          arg = "isShowOnMeta",
          order = 4,
        },
      }
    },
    applyVersionCorrections = {
      type  = "toggle",
      name  = L["Apply version corrections"],
      desc  = L
          ["Correct the version for some items whose release version is different than their usable version. (Keep enabled unless you have a specific reason not to.)"],
      get   = "GetValue",
      set   = "SetValue",
      arg   = "applyVersionCorrections",
      width = "full",
      order = 4,
    },
    tooltipFormatStringGroup = {
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
        tooltipFormatString = {
          type = "input",
          name = "Format",
          desc = L["Provide a template to format the tooltip line"],
          get = "GetValue",
          set = "SetValue",
          arg = "tooltipFormatString",
          width = "full",
          order = 2,
          dialogControl = "ItemVersion-MonoEditBox",
        },
        tooltipFormatStringHelp = {
          type = "group",
          name = L["Format String Tokens"],
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

local function registerMainOptions()
  local optionsName = AddonName .. "Options"
  AceConfig:RegisterOptionsTable(optionsName, OPTIONS_TABLE)
  AceConfigDialog:AddToBlizOptions(optionsName, AddonName)
end

local function registerProfileOptions()
  local profiles = Private.Database:GetProfileOptionsTable()
  local profileOptionsName = AddonName .. "ProfileOptions"
  AceConfig:RegisterOptionsTable(profileOptionsName, profiles)
  AceConfigDialog:AddToBlizOptions(profileOptionsName, "Profiles", AddonName)
end

function Private.Options:Register()
  registerMainOptions()
  registerProfileOptions()
end
