local addonName, ItemVersion = ...

local AceConsole = LibStub("AceConsole-3.0")
local AceGUI = LibStub("AceGUI-3.0")
local API = ItemVersion.API
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
  AceConsole:Print(string.format("%s v%s", addonName, GetAddOnMetadata(addonName, "Version")))
end

function SlashCommandMixin:HandleHelpSubcommand()
  local usage = (
      "\n" ..
          "usage: /itemversion <command>\n" ..
          "\n" ..
          "Available Commands:\n" ..
          "    config  Opens the configuration window\n" ..
          "    issue   Opens a window with information to assist in creating an issue\n" ..
          "    version Displays the version of ItemVersion\n" ..
          "    help    Shows this help"
      )
  AceConsole:Print(usage)
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

local GetFlavor = function()
  local version, build, _, toc = GetBuildInfo()
  local combined = string.format("%s.%s", version, build)
  local flavor = "Unknown flavor"
  if toc >= 100000 then
    flavor = "Retail"
  elseif toc >= 30000 and toc <= 39999 then
    flavor = "Wrath"
  elseif toc <= 10000 then
    flavor = "Classic"
  end
  return string.format("%s (%s)", flavor, combined)
end

local GetPlatform = function()
  local platform = "Unknown platform"
  if IsWindowsClient() then
    platform = "Windows"
  elseif IsMacClient() then
    platform = "Mac"
  elseif IsLinuxClient() then
    platform = "Linux"
  end
  return platform
end

function SlashCommandMixin:HandleIssueSubcommand()
  if self.issueFrame then return end

  local issueFrame = AceGUI:Create("Frame")
  issueFrame:SetCallback("OnClose", function(widget)
    AceGUI:Release(widget)
    self.issueFrame = nil
  end)
  issueFrame:SetTitle(string.format("%s Issue Info", addonName))
  issueFrame:SetLayout("List")
  issueFrame:SetAutoAdjustHeight(true)

  local label = AceGUI:Create("Label")
  label:SetText("Copy and paste this data when making a new issue for ItemVersion.")
  label:SetFont("Fonts\\FRIZQT__.TTF", 14, "")
  label:SetFullWidth(true)
  issueFrame:AddChild(label)

  local flavorAndVersion = AceGUI:Create("EditBox")
  flavorAndVersion:SetLabel("Client flavor and version")
  flavorAndVersion:SetText(GetFlavor())
  flavorAndVersion:SetFullWidth(true)
  flavorAndVersion:DisableButton(true)
  issueFrame:AddChild(flavorAndVersion)

  local itemVersionVersion = AceGUI:Create("EditBox")
  itemVersionVersion:SetLabel("ItemVersion version")
  itemVersionVersion:SetText(GetAddOnMetadata(addonName, "Version"))
  itemVersionVersion:SetFullWidth(true)
  itemVersionVersion:DisableButton(true)
  issueFrame:AddChild(itemVersionVersion)

  local platform = AceGUI:Create("EditBox")
  platform:SetLabel("Platform")
  platform:SetText(GetPlatform())
  platform:SetFullWidth(true)
  platform:DisableButton(true)
  issueFrame:AddChild(platform)

  local url = AceGUI:Create("EditBox")
  url:SetLabel("Issue URL")
  url:SetText("https://github.com/t-mart/ItemVersion/issues/new/choose")
  url:SetFullWidth(true)
  url:DisableButton(true)
  issueFrame:AddChild(url)

  self.issueFrame = issueFrame
end

function SlashCommandMixin:HandleCommand(input)
  local subcommand, nextpos = AceConsole:GetArgs(input)

  local subcommand_handlers = {
    version = self.HandleVersionSubcommand,
    config = self.HandleConfigSubcommand,
    help = self.HandleHelpSubcommand,
    issue = self.HandleIssueSubcommand,
  }

  if not subcommand or subcommand:trim() == "" then
    subcommand = "config"
  elseif not subcommand_handlers[subcommand] then
    subcommand = "help"
  end

  local left = string.sub(input, nextpos)
  subcommand_handlers[subcommand](self, left)
end
