local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)
local AceGUI = LibStub("AceGUI-3.0")
local AceConsole = LibStub("AceConsole-3.0")

-- Define the module container
Private.SlashCommands = {}
local SlashCommands = Private.SlashCommands

local Color = Private.Color

---Get the platform name (Windows, Mac, Linux, or Unknown)
---@return string platform The platform name
local function GetPlatform()
  if IsWindowsClient() then
    return "Windows"
  elseif IsMacClient() then
    return "Mac"
  elseif IsLinuxClient() then
    return "Linux"
  else
    return "Unknown"
  end
end

local usageParts = {
  ["options"] = L["Open options"],
  ["version"] = L["Show version info"],
  ["lookup <item>"] = L["Lookup item ID or Link and print tooltip line"],
  ["help"] = L["Show this message"],
}

---Print the usage information for slash commands
local function PrintUsage()
  AceConsole:Print(L["Usage: /itemversion <command>"])

  for cmd, desc in pairs(usageParts) do
    AceConsole:Print(string.format("  %s - %s", Color.WrapTextWithColor(cmd, Color.Blue()), desc))
  end
end

-- Handlers

---Open the addon options panel
local function HandleOptions()
  LibStub("AceConfigDialog-3.0"):Open(Private.Options.OPTIONS_APP_NAME)
end

---Show the version information window
local function HandleVersion()
  local frame = AceGUI:Create("Frame")
  frame:SetTitle(string.format("%s %s", AddonName, L["Version Information"]))
  frame:SetLayout("List")
  frame:SetWidth(400)
  frame:SetHeight(200)
  frame:SetCallback("OnClose", function(widget)
      AceGUI:Release(widget)
    end
  )

  local version, build, date = GetBuildInfo()

  local text = "" ..
      string.format("%s: %s\n", L["Addon Version"], C_AddOns.GetAddOnMetadata(AddonName, "Version")) ..
      string.format("%s: %s\n", L["WoW Version"], version) ..
      string.format("%s: %s\n", L["WoW Build"], build) ..
      string.format("%s: %s\n", L["WoW Build Date"], date) ..
      string.format("%s: %s\n", L["Platform"], GetPlatform())

  local multiLineEditBox = AceGUI:Create("MultiLineEditBox")
  multiLineEditBox:SetLabel(L["Version Information"])
  multiLineEditBox:SetFullWidth(true)
  multiLineEditBox:SetNumLines(6)
  multiLineEditBox:DisableButton(true)
  multiLineEditBox:SetText(text)
  frame:AddChild(multiLineEditBox)
end

---Handle the lookup slash command to show item version info
---@param itemArg string|nil The item ID or link argument
local function HandleLookup(itemArg)
  if not itemArg then
    AceConsole:Print(L["Must supply an item ID or link to lookup."])
    return
  end

  local itemID = tonumber(itemArg)

  if not itemID then
    -- Try to parse link string: "|Hitem:12345:..."
    local linkId = string.match(itemArg, "item:(%d+)")
    itemID = tonumber(linkId)
  end

  if not itemID then
    AceConsole:Print(L["Invalid item ID or link provided."])
    return
  end

  local API = Private.API
  local profile = Private.Database.profile

  local lookup = API.GetItemVersion(itemID, profile.applyCorrections)
  if not lookup then
    AceConsole:Print(format(L["No version information found for item ID %d"], itemID))
    return
  end

  local formatted = API.FormatTooltip(profile.tooltipFormat, lookup)
  AceConsole:Print(formatted)
end

---Main slash command handler
---@param input string The full command input string
local function SlashHandler(input)
  local command, nextArg = AceConsole:GetArgs(input, 2)

  if not command then
    HandleOptions()
    return
  end

  command = string.lower(command)

  if command == "options" then
    HandleOptions()
  elseif command == "version" then
    HandleVersion()
  elseif command == "lookup" then
    HandleLookup(nextArg)
  else
    -- Unknown command, show help
    PrintUsage()
  end
end

---Initialize and register slash commands
function SlashCommands.Initialize()
  -- Register "/itemversion"
  AceConsole:RegisterChatCommand("itemversion", SlashHandler)
end
