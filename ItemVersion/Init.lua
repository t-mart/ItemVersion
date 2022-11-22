local addonName = ...

ItemVersion = LibStub("AceAddon-3.0"):NewAddon(addonName, "AceConsole-3.0")

function ItemVersion:OnInitialize()
  self.version = GetAddOnMetadata(self.name, "Version")

  self.db = LibStub("AceDB-3.0"):New("ItemVersionDB", ItemVersion:GetDefaultDB())

  LibStub("AceConfig-3.0"):RegisterOptionsTable(self.name, self:GetOptions())

  self:RegisterChatCommand("itemversion", "HandleCommand")

  local _, categoryId = LibStub("AceConfigDialog-3.0"):AddToBlizOptions(self.name)
  self.settingsCategoryId = categoryId

  TooltipDataProcessor.AddTooltipPostCall(Enum.TooltipDataType.Item,
                                          function(...) self:OnTooltipSetItem(...) end)
end

local usage = (
    "\n" ..
        "usage: /itemversion <command>\n" ..
        "\n" ..
        "Available Commands:\n" ..
        "    version Displays the version of ItemVersion\n" ..
        "    config  Opens the configuration window"
    )
local subcommand_handlers = {
  version = "HandleVersionSubcommand",
  config = "HandleConfigSubcommand",
}

function ItemVersion:HandleVersionSubcommand()
  self:Print(string.format("%s v%s", self.name, self.version))
end

function ItemVersion:HandleConfigSubcommand()
  Settings.OpenToCategory(self.settingsCategoryId)
end

function ItemVersion:HandleCommand(input)
  local subcommand, nextpos = self:GetArgs(input)

  if not subcommand or not subcommand_handlers[subcommand] then
    self:Print(usage)
    return
  end

  local left = string.sub(input, nextpos)
  self[subcommand_handlers[subcommand]](self, left)
end
