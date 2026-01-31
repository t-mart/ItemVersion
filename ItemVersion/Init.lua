local AddonName, Private = ...

ItemVersion = LibStub("AceAddon-3.0"):NewAddon(AddonName)

local LSM = LibStub("LibSharedMedia-3.0")

LSM:Register("font", "JetBrains Mono NL",
  "Interface\\AddOns\\" .. AddonName .. "\\Media\\Fonts\\JetBrainsMonoNL-Regular.ttf",
  LSM.LOCALE_BIT_western + LSM.LOCALE_BIT_ruRU)

function ItemVersion:OnInitialize()
  Private.Database:Initialize()

  Private.Options:Register()

  self.API = Private.API

  -- self.tooltip = self.Tooltip:New(self.Database)
  Private.Tooltip:HookTooltip()

  -- self.slashCommand = self.SlashCommand:New(addonName, self.RegisterChatCommand)
  -- self.slashCommand:Register()
end
