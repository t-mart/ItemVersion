local addonName, ItemVersion = ...

local L = LibStub("AceLocale-3.0"):GetLocale(addonName)

function ItemVersion:GetDefaultDB()
  return {
    profile = {
      showPrefix = true,
      prefixColor = { r = 1.0, g = 1.0, b = 1.0 },
      shortExpacNames = false,
      expacColor = { r = 1.0, g = 1.0, b = 1.0 },
      showVersion = true,
      versionColor = { r = 1.0, g = 1.0, b = 1.0 },
      showWhenMissing = false,
      keyModifiers = { shift = false, control = false, alt = false, meta = false },
      includeCommunityUpdates = true,
    }
  }
end

local function CombineTables(...)
  local combined = {}
  for _, tbl in ipairs(SafePack(...)) do
    for k, v in pairs(tbl) do
      combined[k] = v;
    end
  end
  return combined
end

function ItemVersion:_UpdatePreviews()
  local optionsTable = LibStub("AceConfigRegistry-3.0"):GetOptionsTable(self.name, "dialog",
                                                                        self.name .. "-1.0")
  optionsTable.args.tooltip.args.preview.name = self:PreviewTooltipText()
end

function ItemVersion:_SetScalarOptFn(varname)
  return function(_, value)
    self.db.profile[varname] = value
    self:_UpdatePreviews()
  end
end

function ItemVersion:_GetScalarOptFn(varname)
  return function()
    return self.db.profile[varname]
  end
end

function ItemVersion:_SetOptColorFn(varname)
  return function(_, r, g, b)
    self.db.profile[varname] = { r = r, g = g, b = b }
    self:_UpdatePreviews()
  end
end

function ItemVersion:_GetOptColorFn(varname)
  return function()
    local c = self.db.profile[varname]
    return c.r, c.g, c.b
  end
end

function ItemVersion:PreviewTooltipText()
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
    table.insert(mapped, self:TooltipLineForItemId(id))
  end
  return table.concat(mapped, "\n\n")
end

function ItemVersion:GetOptions()
  local modifierKeyValues = { shift = L["SHIFT"], control = L["CONTROL"], alt = L["ALT"] }
  if IsMacClient() then
    -- call this CMD, which matches Mac vernacular better than META
    modifierKeyValues.meta = L["CMD"]
  end
  local options = {
    name = self.name,
    handler = self,
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
            desc = L["Including community updates changes some items' version/expansion to the one " ..
            "that players expect. For example, the herb [Marrowroot] was actually added towards " ..
            "the end of BfA in pre-release development, but was only obtainable in SL. With this " ..
            "option turned on, ItemVersion would report SL in this case, instead of BfA.\n\n" ..
            "Because the updates are non-canonical, the version number will be a placeholder one: " ..
            "the major part will be that of the new expansion, but the lesser parts will be zeroed.\n\n" ..
            "If you encounter an item that is not fixed by these updates, please consider " ..
            "reporting it to the project page."],
            set = self:_SetScalarOptFn("includeCommunityUpdates"),
            get = self:_GetScalarOptFn("includeCommunityUpdates"),
            width = "full",
          },
          showWhenMissing = {
            type = "toggle",
            order = 7,
            name = L["Show for unknown items"],
            desc = L["Show the tooltip line even when the item is not in the database"],
            set = self:_SetScalarOptFn("showWhenMissing"),
            get = self:_GetScalarOptFn("showWhenMissing"),
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
                set = self:_SetScalarOptFn("showPrefix"),
                get = self:_GetScalarOptFn("showPrefix"),
              },
              prefixColor = {
                type = "color",
                order = 20,
                name = L["Prefix color"],
                desc = L["The color of the prefix"],
                set = self:_SetOptColorFn("prefixColor"),
                get = self:_GetOptColorFn("prefixColor"),
                disabled = function() return self.db.profile.showPrefix == false end,
              },
            }
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
                set = self:_SetScalarOptFn("shortExpacNames"),
                get = self:_GetScalarOptFn("shortExpacNames"),
                width = "double"
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
                set = self:_SetOptColorFn("expacColor"),
                get = self:_GetOptColorFn("expacColor"),
              },
            }
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
                set = self:_SetScalarOptFn("showVersion"),
                get = self:_GetScalarOptFn("showVersion"),
              },
              versionColor = {
                type = "color",
                order = 41,
                name = L["Version color"],
                desc = L["The color of the version"],
                set = self:_SetOptColorFn("versionColor"),
                get = self:_GetOptColorFn("versionColor"),
                disabled = function() return self.db.profile.showVersion == false end,
              },
            }
          },
          keyModifiers = {
            type = "multiselect",
            order = 30,
            name = L["Modifier keys"],
            desc = L[
                "Display the tooltip only when the selected modifier keys being are " ..
                    "pressed. (No selections means always show.)"
                ],
            values = modifierKeyValues,
            set = function(_, key, value) self.db.profile.keyModifiers[key] = value end,
            get = function(...) return self.db.profile.keyModifiers[select(-1, ...)] end,
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
            name = self:PreviewTooltipText(),
          },
        }
      },
      profile = CombineTables(LibStub("AceDBOptions-3.0"):GetOptionsTable(self.db), { order = 100 })
    }
  }

  return options
end
