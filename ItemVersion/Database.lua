local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)

---@class DatabaseProfile
---@field lineColor Color The color of the tooltip line
---@field showOnShift boolean Show tooltip when Shift is held
---@field showOnControl boolean Show tooltip when Control is held
---@field showOnAlt boolean Show tooltip when Alt is held
---@field showOnMeta boolean Show tooltip when Meta/Cmd is held (Mac only)
---@field applyCorrections boolean Whether to apply version corrections
---@field tooltipFormat string The format string for the tooltip
---@field version number The profile version number

Private.DatabaseManager = {}
local Color = Private.Color

local NAME = "ItemVersionDB"
local CURRENT_VERSION_NUMBER = 1

local VERSION_DEFAULTS = {
  -- back before versioning
  ["nil"] = {
    profile = {
      showPrefix = true,
      prefixColor = Color.White(),
      shortExpacNames = false,
      expacColor = Color.White(),
      showVersion = true,
      versionColor = Color.White(),
      showWhenMissing = false,
      showBuildNumber = true,
      keyModifiers = { shift = false, control = false, alt = false, meta = false },
      includeCommunityUpdates = true,
    },
  },
  [1] = {
    profile = {
      lineColor = Color.White(),
      showOnShift = false,
      showOnControl = false,
      showOnAlt = false,
      showOnMeta = false,
      applyCorrections = true,
      tooltipFormat = L["Added in {expacIcon} ({versionTriple})"],
      version = 1,
    }
  },
  [2] = {
    profile = {
      enableTooltip = true,
      lineColor = Color.White(),
      showOnShift = false,
      showOnControl = false,
      showOnAlt = false,
      showOnMeta = false,
      applyCorrections = true,
      tooltipFormat = L["Added in {expacIcon} ({versionTriple})"],
      version = 1,
    },
  }
}

local CURRENT_VERSION_DEFAULTS = VERSION_DEFAULTS[CURRENT_VERSION_NUMBER]

---Migrates a database profile to the current version
---@param database table The AceDB database object
local function migrate(database)
  local profile = database.profile

  if profile.version == nil then
    -- from nil to version 1
    local target_defaults = VERSION_DEFAULTS[1].profile
    profile.lineColor = Color.White()
    profile.showOnShift = profile.keyModifiers.shift
    profile.showOnControl = profile.keyModifiers.control
    profile.showOnAlt = profile.keyModifiers.alt
    profile.showOnMeta = profile.keyModifiers.meta
    profile.applyCorrections = profile.includeCommunityUpdates
    profile.tooltipFormat = target_defaults.tooltipFormat
    profile.version = 1
    Private.Table.KeepOnlyKnownKeys(profile, target_defaults)
  end

  if profile.version == 1 then
    -- from version 1 to version 2
    local target_defaults = VERSION_DEFAULTS[2].profile
    profile.enableTooltip = true
    profile.version = 2
    Private.Table.KeepOnlyKnownKeys(profile, target_defaults)
  end

  -- if profile.version == 2 then
  --   -- future migrations would go here
  -- end

  if profile.version ~= CURRENT_VERSION_NUMBER then
    error(("Profile version %d is not supported by this version of ItemVersion. Please update your profile or reset to defaults."):format(profile.version))
  end
end

---Initialize the database and apply migrations
---@return table database The initialized AceDB database
function Private.DatabaseManager.Initialize()
  if Private.Database then return Private.Database end

  local database = LibStub("AceDB-3.0"):New(NAME, CURRENT_VERSION_DEFAULTS, true)

  migrate(database)

  Private.Database = database

  -- when profile changes, migrate to ensure schema
  ---@param _ string
  ---@param db table
  local function migrateCallback(_, db)
    migrate(db)
  end
  database.RegisterCallback(Private.Database, "OnProfileChanged", migrateCallback)
  database.RegisterCallback(Private.Database, "OnProfileCopied", migrateCallback)
  database.RegisterCallback(Private.Database, "OnProfileReset", migrateCallback)

  -- return in case caller wants it, but by and large, use Private.Database for access
  return database
end

---Get the AceDBOptions table for profile management
---@return table options The profile options table
function Private.DatabaseManager.GetProfileOptionsTable()
  return LibStub("AceDBOptions-3.0"):GetOptionsTable(Private.Database)
end
