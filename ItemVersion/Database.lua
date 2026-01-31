local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)

Private.Database = {}

local DB_NAME = "ItemVersionDB"

-- We define the default profile versions as a list first
-- (_DEFAULT_PROFILE_VERSIONS), then we build a map from the profile's version
-- number to the profile itself (DEFAULT_PROFILES_BY_VERSION). This is a little
-- bit of a runaround, but it ensures we don't need to repeat the version numbers as
-- both the key and inside the profile, which reduces the chance of errors.
local _DEFAULT_PROFILE_VERSIONS = {
  -- the "nil" default profile is what we used before we had versioning
  -- might not need to keep this in practice, but leaving for documentation
  {
    profile = {
      showPrefix = true,
      prefixColor = { r = 1.0, g = 1.0, b = 1.0 },
      shortExpacNames = false,
      expacColor = { r = 1.0, g = 1.0, b = 1.0 },
      showVersion = true,
      versionColor = { r = 1.0, g = 1.0, b = 1.0 },
      showWhenMissing = false,
      showBuildNumber = true,
      keyModifiers = { shift = false, control = false, alt = false, meta = false },
      includeCommunityUpdates = true,
    },
  },
  {
    profile = {
      tokenColor = { r = 1.0, g = 1.0, b = 1.0 },
      isShowOnShift = false,
      isShowOnControl = false,
      isShowOnAlt = false,
      isShowOnMeta = false,
      applyVersionCorrections = true,
      tooltipFormatString = L["Added in {expacIcon} ({versionTriple})"],
      version = 1,
    },
  }
}
local DEFAULT_PROFILES_BY_VERSION = {}
for _, version in pairs(_DEFAULT_PROFILE_VERSIONS) do
  local profileVersion = version.profile.version or 0
  DEFAULT_PROFILES_BY_VERSION[profileVersion] = version
end
local CURRENT_DB_VERSION = 1
local DEFAULT_PROFILE = DEFAULT_PROFILES_BY_VERSION[CURRENT_DB_VERSION]
local db

local function migrate()
  local old
  
  if db.profile.version == nil then
    -- from nil to version 1
    old = db.profile
    db.profile = Private.Util.DeepCopy(DEFAULT_PROFILES_BY_VERSION[1].profile)
    db.profile.isShowOnShift = old.keyModifiers.shift
    db.profile.isShowOnControl = old.keyModifiers.control
    db.profile.isShowOnAlt = old.keyModifiers.alt
    db.profile.isShowOnMeta = old.keyModifiers.meta
    db.profile.applyVersionCorrections = old.includeCommunityUpdates
  end

  if db.profile.version == 1 then
    -- future migrations go here
  end
end

function Private.Database:Initialize()
  db = LibStub("AceDB-3.0"):New(DB_NAME, DEFAULT_PROFILE, true)
  migrate()
end

function Private.Database:GetValue(key)
  return db.profile[key]
end

function Private.Database:SetValue(key, value)
  db.profile[key] = value
end

function Private.Database:ResetValue(key)
  db.profile[key] = DEFAULT_PROFILE.profile[key]
end

-- Get profile options table for AceConfig
function Private.Database:GetProfileOptionsTable()
  return LibStub("AceDBOptions-3.0"):GetOptionsTable(db)
end
