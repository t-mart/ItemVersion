local AddonName, Private = ...

ItemVersion = LibStub("AceAddon-3.0"):NewAddon(AddonName)

local LSM = LibStub("LibSharedMedia-3.0")

LSM:Register("font", "JetBrains Mono NL",
  "Interface\\AddOns\\" .. AddonName .. "\\Media\\Fonts\\JetBrainsMonoNL-Regular.ttf",
  LSM.LOCALE_BIT_western + LSM.LOCALE_BIT_ruRU)

---Initialize the addon
function ItemVersion:OnInitialize()
  Private.DatabaseManager.Initialize()

  Private.Options.Register()

  self.API = Private.API

  Private.Tooltip.HookTooltip()

  Private.SlashCommands.Initialize()
end
