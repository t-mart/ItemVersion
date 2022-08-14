local AddonName = ...

local version = GetAddOnMetadata(AddonName, "Version")

-- slash command to get version of ItemVersion
SLASH_ITEMVERSION1 = "/itemversion"

function SlashCmdList.ITEMVERSION()
  print(AddonName .. " v" .. version)
end

-- create global table and expose version
ItemVersion = {
  version = version
}
