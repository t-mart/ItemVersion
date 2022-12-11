local addonName, ItemVersion = ...

local L = LibStub("AceLocale-3.0"):GetLocale(addonName)
local AceConfig = LibStub("AceConfig-3.0")
local AceConfigDialog = LibStub("AceConfigDialog-3.0")
local AceDBOptions = LibStub("AceDBOptions-3.0")
local Util = ItemVersion.Util

local GetPreviewTooltipText = function(tooltip)
  local exampleItems = {
    159, -- Refreshing Spring Water, classic
    22786, -- Dreaming Glory, tbc
    36905, -- Lichbloom, wotlk
    52985, -- Azshara's Veil, cata
    72238, -- Golden Lotus, mop
    120945, -- Primal Spirit, wod
    124124, -- Blood of Sargeras, legion
    163036, -- Polished Pet Charm, bfa
    182614, -- Blanchy's Reins, sl
    191470, -- Writhebark, df
    0, -- unknown item
  }
  local mapped = {}
  for _, id in pairs(exampleItems) do
    table.insert(mapped, tooltip:GenerateLineForItemId(id))
  end
  return table.concat(mapped, "\n\n")
end

local ScalarOption = function(db, varname, updatePreviewFn)
  return {
    get = function()
      return db.profile[varname]
    end,
    set = function(_, value)
      db.profile[varname] = value
      updatePreviewFn()
    end,
  }
end

local ColorOption = function(db, varname, updatePreviewFn)
  return {
    get = function()
      local color = db.profile[varname]
      return color.r, color.g, color.b
    end,
    set = function(_, r, g, b)
      db.profile[varname] = { r = r, g = g, b = b }
      updatePreviewFn()
    end,
  }
end

local MultiselectOption = function(db, varname, values, updatePreviewFn)
  return {
    values = values,
    get = function(...)
      return db.profile[varname][select(-1, ...)] -- strangely defined as the last argument passed
    end,
    set = function(_, key, value)
      db.profile[varname][key] = value
      updatePreviewFn()
    end,
  }
end

local GetOptions = function(db, tooltip)
  local options = {}

  local modifierKeyValues = { shift = L["SHIFT"], control = L["CONTROL"], alt = L["ALT"] }
  if IsMacClient() then
    -- call this CMD, which matches Mac vernacular better than META
    modifierKeyValues.meta = L["CMD"]
  end

  local updatePreview = function()
    -- the following options table structure does not yet exist, but it will by the time this
    -- function is called in the option setters.
    options.args.tooltip.args.preview.name = GetPreviewTooltipText(tooltip)
  end

  local includeCommunityUpdatesOpt = ScalarOption(db, "includeCommunityUpdates", updatePreview)
  local showWhenMissingOpt = ScalarOption(db, "showWhenMissing", updatePreview)
  local showPrefixOpt = ScalarOption(db, "showPrefix", updatePreview)
  local prefixColorOpt = ColorOption(db, "prefixColor", updatePreview)
  local shortExpacNamesOpt = ScalarOption(db, "shortExpacNames", updatePreview)
  local expacColorOpt = ColorOption(db, "expacColor", updatePreview)
  local showVersionOpt = ScalarOption(db, "showVersion", updatePreview)
  local versionColorOpt = ColorOption(db, "versionColor", updatePreview)
  local keyModifiersOpt = MultiselectOption(db, "keyModifiers", modifierKeyValues, updatePreview)

  Util.Mixin(options, {
    name = addonName,
    -- handler = self,
    type = "group",
    inline = true,
    args = {
      tooltip = {
        type = "group",
        name = L["Tooltip"],
        order = 10,
        args = {
          includeCommunityUpdates = {
            type = "toggle",
            order = 5,
            name = L["Include community updates"],
            desc = L["Including community updates changes some items' version/expansion to the one that players expect. For example, the herb [Marrowroot] was actually added towards the end of BfA in pre-release development, but was only obtainable in SL. With this option turned on, ItemVersion would report SL in this case, instead of BfA.\n\nBecause the updates are non-canonical, the version number will be a placeholder one: the major part will be that of the new expansion, but the lesser parts will be zeroed.\n\nIf you encounter an item that is not fixed by these updates, please consider reporting it to the project page."],
            set = includeCommunityUpdatesOpt.set,
            get = includeCommunityUpdatesOpt.get,
            width = "full",
          },
          showWhenMissing = {
            type = "toggle",
            order = 7,
            name = L["Show for unknown items"],
            desc = L["Show the tooltip line even when the item is not in the database"],
            set = showWhenMissingOpt.set,
            get = showWhenMissingOpt.get,
            width = "full",
          },
          prefix = {
            order = 10,
            type = "group",
            guiInline = true,
            name = L["Prefix"],
            args = {
              showPrefix = {
                type = "toggle",
                order = 10,
                name = L["Show prefix"],
                desc = L["Prefix the tooltip line with a label"],
                set = showPrefixOpt.set,
                get = showPrefixOpt.get,
              },
              prefixColor = {
                type = "color",
                order = 20,
                name = L["Prefix color"],
                desc = L["The color of the prefix"],
                set = prefixColorOpt.set,
                get = prefixColorOpt.get,
                disabled = function()
                  return db.profile.showPrefix == false
                end,
              },
            },
          },
          expac = {
            order = 11,
            type = "group",
            guiInline = true,
            name = L["Expansion"],
            args = {
              shortExpacNames = {
                type = "toggle",
                order = 20,
                name = L["Use short expansion names"],
                desc = L["Abbreviate the item's expansion"],
                set = shortExpacNamesOpt.set,
                get = shortExpacNamesOpt.get,
                width = "double",
              },
              expac_newline = {
                order = 21,
                type = "description",
                name = "",
              },
              expacColor = {
                type = "color",
                order = 30,
                name = " " .. L["Expansion color"], -- strange alignment issue
                desc = L["The color of the expansion"],
                set = expacColorOpt.set,
                get = expacColorOpt.get,
              },
            },
          },
          version = {
            order = 20,
            type = "group",
            guiInline = true,
            name = L["Version"],
            args = {
              showVersion = {
                type = "toggle",
                order = 40,
                name = L["Show version"],
                desc = L["Show the version in which the item was added"],
                set = showVersionOpt.set,
                get = showVersionOpt.get,
              },
              versionColor = {
                type = "color",
                order = 41,
                name = L["Version color"],
                desc = L["The color of the version"],
                set = versionColorOpt.set,
                get = versionColorOpt.get,
                disabled = function()
                  return db.profile.showVersion == false
                end,
              },
            },
          },
          keyModifiers = {
            type = "multiselect",
            order = 30,
            name = L["Modifier keys"],
            desc = L["Display the tooltip only when the selected modifier keys being are pressed. (No selections means always show.)"],
            values = keyModifiersOpt.values,
            set = keyModifiersOpt.set,
            get = keyModifiersOpt.get,
            width = "full",
          },
          previewHeader = {
            type = "header",
            order = 60,
            name = L["Preview"],
            width = "full",
          },
          preview = {
            order = 61,
            type = "description",
            fontSize = "medium",
            name = GetPreviewTooltipText(tooltip),
          },
        },
      },
      profile = Util.Mixin(AceDBOptions:GetOptionsTable(db), { order = 100 }),
    },
  })

  return options
end

local OptionsMixin = {}

ItemVersion.Options = {}

function ItemVersion.Options:New(db, tooltip)
  local t = {
    options = GetOptions(db, tooltip),
  }

  return Util.Mixin(t, OptionsMixin)
end

function OptionsMixin:Register()
  AceConfig:RegisterOptionsTable(addonName, self.options)
end

function OptionsMixin:AddToBlizOptions()
  local _, categoryId = AceConfigDialog:AddToBlizOptions(addonName, addonName, nil, "tooltip")
  local settingsCategoryId = categoryId
  AceConfigDialog:AddToBlizOptions(addonName, "Profiles", categoryId, "profile")

  return settingsCategoryId -- return the main settings category id
end
