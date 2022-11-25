local addonName, addon = ...

-- pass in the `addon` table: AceAddon will use it instead of creating a new table
-- this is important because our Data.lua file inserts into that addon table too
ItemVersion = LibStub("AceAddon-3.0"):NewAddon(addon, addonName, "AceConsole-3.0")

function ItemVersion:OnInitialize()
  self.version = GetAddOnMetadata(self.name, "Version")

  self.db = LibStub("AceDB-3.0"):New("ItemVersionDB", self:GetDefaultDB(), true)

  LibStub("AceConfig-3.0"):RegisterOptionsTable(self.name, self:GetOptions())

  self:RegisterChatCommand("itemversion", function(...) self:HandleCommand(...) end)

  local _, categoryId = LibStub("AceConfigDialog-3.0"):AddToBlizOptions(self.name, self.name, nil, "tooltip")
  self.settingsCategoryId = categoryId

  LibStub("AceConfigDialog-3.0"):AddToBlizOptions(self.name, "Profiles", categoryId, "profile")

  self:HookTooltipCall()
  -- TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item,
  --                                         function(...) self:OnTooltipSetItem(...) end)
end
