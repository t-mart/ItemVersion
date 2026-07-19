local Private = require("helper").load()
local Tokens = Private.Tokens

-- A lookup shaped like the ones API builds, with fields chosen so every token
-- resolves to something recognizable.
local function makeLookup()
  return {
    expansion = {
      major = 3,
      canonName = "Wrath of the Lich King",
      shortName = "WotLK",
      texture = "Interface\\Icons\\Sample",
    },
    minor = 2,
    patch = 5,
    build = 12340,
  }
end

local function resolverFor(tokenString)
  for _, info in ipairs(Tokens) do
    if info.string == tokenString then
      return info.resolve
    end
  end
  return nil
end

describe("Tokens", function()
  local lookup = makeLookup()

  local cases = {
    ["{expacFull}"] = "Wrath of the Lich King",
    ["{expacShort}"] = "WotLK",
    ["{expacIcon}"] = "|TInterface\\Icons\\Sample:16:32|t",
    ["{versionFull}"] = "3.2.5.12340",
    ["{versionTriple}"] = "3.2.5",
    ["{buildNumber}"] = "12340",
  }

  for tokenString, expected in pairs(cases) do
    it("resolves " .. tokenString, function()
      local resolve = resolverFor(tokenString)
      assert.is_not_nil(resolve)
      assert.are.equal(expected, resolve(lookup))
    end)
  end

  it("has a resolver for every token, with no duplicates", function()
    local seen = {}
    for _, info in ipairs(Tokens) do
      assert.is_function(info.resolve)
      assert.is_nil(seen[info.string], "duplicate token " .. tostring(info.string))
      seen[info.string] = true
    end
  end)
end)
