local Private = require("helper").load()
local Expansion = Private.Expansion

describe("Expansion:GetExpansionFromMajor", function()
  it("returns the expansion whose major matches", function()
    for _, expected in ipairs(Expansion.All) do
      local got = Expansion:GetExpansionFromMajor(expected.major)
      assert.are.equal(expected, got)
    end
  end)

  it("returns nil for a major no expansion claims", function()
    assert.is_nil(Expansion:GetExpansionFromMajor(0))
    assert.is_nil(Expansion:GetExpansionFromMajor(9999))
  end)
end)

describe("Expansion:GetCorrectedExpansionForItemId", function()
  -- Pull a real correction out of the source data rather than hardcoding ids that
  -- may change.
  local corrected, owner
  for _, expansion in ipairs(Expansion.All) do
    if expansion.corrections and expansion.corrections[1] then
      corrected = expansion.corrections[1]
      owner = expansion
      break
    end
  end

  it("has at least one corrected item to exercise", function()
    assert.is_not_nil(corrected)
  end)

  it("maps a corrected item id to the expansion that lists it", function()
    assert.are.equal(owner, Expansion:GetCorrectedExpansionForItemId(corrected))
  end)

  it("returns nil for an item id with no correction", function()
    assert.is_nil(Expansion:GetCorrectedExpansionForItemId(-1))
  end)
end)
