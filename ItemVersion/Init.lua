local AddonName, _ = ...

ItemVersion = {}

ItemVersion.version = GetAddOnMetadata(AddonName, "Version")


-- slash command to get version of ItemVersion
SLASH_ITEMVERSION1 = '/itemversion'

function SlashCmdList.ITEMVERSION()
  print("ItemVersion v" .. ItemVersion.version)
end
