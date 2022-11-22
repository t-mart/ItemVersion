local addonName = ...

ItemVersion = LibStub("AceAddon-3.0"):GetAddon(addonName)
local L = LibStub("AceLocale-3.0"):GetLocale(addonName)

function ItemVersion:GetDefaultDB()
  return {
    profile = {
      showPrefix = true,
      prefixColor = { r = 1.0, g = 1.0, b = 1.0},
      shortExpacNames = false,
      expacColor = { r = 1.0, g = 1.0, b = 1.0},
      showVersion = true,
      versionColor = { r = 1.0, g = 1.0, b = 1.0},
      showWhenMissing = false,
    }
  }
end

local function packRGBTable(...)
  local r, g, b, a = ...
  return { r = r, g = g, b = b}
end

local function unpackRGBTable(tbl)
  return tbl.r, tbl.g, tbl.b, tbl.a
end

local function CombineTables(...)
  local combined = {}
  for i, tbl in ipairs(SafePack(...)) do
    for k, v in pairs(tbl) do
      combined[k] = v;
    end
  end
  return combined
end

function ItemVersion:GetOptions()
  local options = {
    name = self.name,
    handler = self,
    type = "group",
    inline = true,
    args = {
      tooltipGroup = {
        type = "group",
        name = L["Tooltip"],
        order = 10,
        args = {
          showPrefix = {
            type = "toggle",
            order = 10,
            name = L["Show prefix"],
            desc = L["Prefix the tooltip line with a label"],
            set = function(_, value) self.db.profile.showPrefix = value end,
            get = function() return self.db.profile.showPrefix end,
            width = "normal",
          },
          prefixColor = {
            type = "color",
            order = 11,
            name = L["Prefix color"],
            desc = L["The color of the prefix"],
            set = function(_, ...) self.db.profile.prefixColor = packRGBTable(...) end,
            get = function() return unpackRGBTable(self.db.profile.prefixColor) end,
            disabled = function() return self.db.profile.showPrefix == false end,
            width = "normal",
          },
          shortExpacNames = {
            type = "toggle",
            order = 20,
            name = L["Use short expansion names"],
            desc = L["Abbreviate the item's expansion"],
            set = function(_, value) self.db.profile.shortExpacNames = value end,
            get = function() return self.db.profile.shortExpacNames end,
            width = "full",
          },
          expacColor = {
            type = "color",
            order = 30,
            name = L["Expansion color"],
            desc = L["The color of the expansion"],
            set = function(_, ...) self.db.profile.expacColor = packRGBTable(...) end,
            get = function() return unpackRGBTable(self.db.profile.expacColor) end,
            width = "full",
          },
          showVersion = {
            type = "toggle",
            order = 40,
            name = L["Show version"],
            desc = L["Show the version in which the item was added"],
            set = function(_, value) self.db.profile.showVersion = value end,
            get = function() return self.db.profile.showVersion end,
            width = "normal",
          },
          versionColor = {
            type = "color",
            order = 41,
            name = L["Version color"],
            desc = L["The color of the version"],
            set = function(_, ...) self.db.profile.versionColor = packRGBTable(...) end,
            get = function() return unpackRGBTable(self.db.profile.versionColor) end,
            disabled = function() return self.db.profile.showVersion == false end,
            width = "normal",
          },
          showWhenMissing = {
            type = "toggle",
            order = 50,
            name = L["Show when item missing"],
            desc = L["Show the tooltip line even when the item is missing from the database"],
            set = function(_, value) self.db.profile.showWhenMissing = value end,
            get = function() return self.db.profile.showWhenMissing end,
            width = "full",
          },
        }
      },
      profile = CombineTables(LibStub("AceDBOptions-3.0"):GetOptionsTable(self.db), { order = 100 })
    }
  }

  return options
end
