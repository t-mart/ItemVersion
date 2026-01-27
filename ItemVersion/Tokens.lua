local AddonName, Private = ...

local L = LibStub("AceLocale-3.0"):GetLocale(AddonName)

---@class TokenInfo
---@field string string The token string (e.g., "{expacLong}")
---@field description string The human-readable description of the token
---@field resolve fun(lookup: ItemVersionLookup): string Function to resolve the token to its value

---@type TokenInfo[]
Private.Tokens = {
    {
        string = "{expacFull}",
        description = L["Full name of the expansion"],
        resolve = function(lookup)
            return lookup.expansion.canonName
        end,
    },
    {
        string = "{expacShort}",
        description = L["Short name of the expansion"],
        resolve = function(lookup)
            return lookup.expansion.shortName
        end,
    },
    {
        string = "{expacIcon}",
        description = L["Expansion icon"],
        resolve = function(lookup)
            local expansion = Private.Expansion:GetExpansionFromMajor(lookup.expansion.major)
            return format("|T%s:16:32|t", expansion.texture)
        end,
    },
    {
        string = "{versionFull}",
        description = L["Full version"],
        resolve = function(lookup)
            return format("%d.%d.%d.%d", lookup.expansion.major, lookup.minor, lookup.patch, lookup.build)
        end,
    },
    {
        string = "{versionTriple}",
        description = L["Major, minor, and patch version"],
        resolve = function(lookup)
            return format("%d.%d.%d", lookup.expansion.major, lookup.minor, lookup.patch)
        end,
    },
    {
        string = "{buildNumber}",
        description = L["Build number only"],
        resolve = function(lookup)
            return tostring(lookup.build)
        end,
    }
}
