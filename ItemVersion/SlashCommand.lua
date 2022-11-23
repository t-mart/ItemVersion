local addonName, ItemVersion = ...

local L = LibStub("AceLocale-3.0"):GetLocale(addonName)

local subcommand_handlers = {
  version = "HandleVersionSubcommand",
  config = "HandleConfigSubcommand",
  help = "HandleHelpSubcommand",
}

function ItemVersion:HandleVersionSubcommand()
  self:Print(string.format("%s v%s", self.name, self.version))
end

function ItemVersion:HandleHelpSubcommand()
  local usage = (
    "\n" ..
        "usage: /itemversion <command>\n" ..
        "\n" ..
        "Available Commands:\n" ..
        "    config  Opens the configuration window\n" ..
        "    version Displays the version of ItemVersion\n" ..
        "    help    Shows this help"
    )
  self:Print(usage)
end

function ItemVersion:HandleConfigSubcommand()
  Settings.OpenToCategory(self.settingsCategoryId)
end

function ItemVersion:HandleCommand(input)
  local subcommand, nextpos = self:GetArgs(input)

  if not subcommand or subcommand:trim() == "" then
    subcommand = "config"
  elseif not subcommand_handlers[subcommand] then
    subcommand = "help"
  end


  local left = string.sub(input, nextpos)
  self[subcommand_handlers[subcommand]](self, left)
end
