local addonName, addon = ...

-- pass in the `addon` table: AceAddon will use it instead of creating a new table
-- this is important because our Data.lua file inserts into that addon table too
ItemVersion = LibStub("AceAddon-3.0"):NewAddon(addon, addonName)

function ItemVersion:OnInitialize()
  self.db = self.Database:New()

  self.tooltip = self.Tooltip:New(self.db)
  self.tooltip:HookTooltipCall()

  self.options = self.Options:New(self.db, self.tooltip)
  self.options:Register()
  local settingsCategoryId = self.options:AddToBlizOptions()

  self.slashCommand = self.SlashCommand:New(settingsCategoryId, self.RegisterChatCommand)
  self.slashCommand:Register()
end
