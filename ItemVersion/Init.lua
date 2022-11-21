local AddonName = ...

local version = GetAddOnMetadata(AddonName, "Version")

local slash_command = function(msg)
  print(AddonName .. " v" .. version)
end

RegisterNewSlashCommand(slash_command, "itemversion", "")

-- create global table and expose version
ItemVersion = {
  version = version
}
