local addonName, ItemVersion = ...

local AceConsole = LibStub("AceConsole-3.0")
local Util = ItemVersion.Util

local SlashCommandMixin = {}

ItemVersion.SlashCommand = {}

function ItemVersion.SlashCommand:New(settingsCategoryId, registerChatCommand)
  local t = {
    settingsCategoryId = settingsCategoryId,
    registerChatCommand = registerChatCommand,
  }

  return Util.Mixin(t, SlashCommandMixin)
end

function SlashCommandMixin:Register()
  AceConsole:RegisterChatCommand("itemversion", function(...) self:HandleCommand(...) end)
end

function SlashCommandMixin:HandleVersionSubcommand()
  self:Print(string.format("%s v%s", addonName, GetAddOnMetadata(addonName, "Version")))
end

function SlashCommandMixin:HandleHelpSubcommand()
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

function SlashCommandMixin:HandleConfigSubcommand()
  if Settings then
    -- mainline way
    Settings.OpenToCategory(self.settingsCategoryId)
  else
    -- classic way
    -- lol, this isn't a bug: gotta do it twice.
    InterfaceOptionsFrame_OpenToCategory(addonName)
    InterfaceOptionsFrame_OpenToCategory(addonName)
  end
end

function SlashCommandMixin:HandleCommand(input)
  local subcommand, nextpos = AceConsole:GetArgs(input)

  local subcommand_handlers = {
    version = self.HandleVersionSubcommand,
    config = self.HandleConfigSubcommand,
    help = self.HandleHelpSubcommand,
  }

  if not subcommand or subcommand:trim() == "" then
    subcommand = "config"
  elseif not subcommand_handlers[subcommand] then
    subcommand = "help"
  end

  local left = string.sub(input, nextpos)
  subcommand_handlers[subcommand](self, left)
end
