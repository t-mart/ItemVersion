local helper = require("helper")
local Private = helper.load()
local API = Private.API

local runs = helper.reconstructRuns(Private)
local knownMajors = helper.knownMajors(Private)

local function versionRow(versionId)
  return Private.versionIdToVersion[versionId + 1]
end

-- A covered id whose major maps to a real expansion, plus the row it should resolve
-- to. Derived from the data so it survives a database refresh.
local presentId, presentRow
for _, run in ipairs(runs) do
  local row = versionRow(run.versionId)
  if row and knownMajors[row[1]] then
    presentId = run.start
    presentRow = row
    break
  end
end

describe("API.GetItemVersion lookup", function()
  it("has a present item to exercise", function()
    assert.is_not_nil(presentId)
  end)

  it("resolves a covered item to its version row", function()
    local v = API.GetItemVersion(presentId, false)

    assert.is_not_nil(v)
    assert.are.equal(presentId, v.itemId)
    assert.are.equal(presentRow[1], v.expansion.major)
    assert.are.equal(presentRow[2], v.minor)
    assert.are.equal(presentRow[3], v.patch)
    assert.are.equal(presentRow[4], v.build)
    assert.is_false(v.isCorrected)
  end)

  it("resolves the first and last covered ids", function()
    assert.is_not_nil(API.GetItemVersion(runs[1].start, false))

    local last = runs[#runs]
    assert.is_not_nil(API.GetItemVersion(last.start + last.length - 1, false))
  end)

  it("returns nil past the end of the data", function()
    local last = runs[#runs]
    assert.is_nil(API.GetItemVersion(last.start + last.length, false))
  end)

  it("returns nil for a non-positive id", function()
    assert.is_nil(API.GetItemVersion(-1, false))
    assert.is_nil(API.GetItemVersion(0, false))
  end)

  it("returns nil for an id that falls in a gap between runs", function()
    local gapId
    for i = 1, #runs - 1 do
      local afterRun = runs[i].start + runs[i].length
      if afterRun < runs[i + 1].start then
        gapId = afterRun
        break
      end
    end

    assert.is_not_nil(gapId, "expected the data to contain at least one gap")
    assert.is_nil(API.GetItemVersion(gapId, false))
  end)
end)

describe("API.GetItemVersion corrections", function()
  local correctedId, owner
  for _, expansion in ipairs(Private.Expansion.All) do
    if expansion.corrections and expansion.corrections[1] then
      correctedId = expansion.corrections[1]
      owner = expansion
      break
    end
  end

  it("has a corrected item to exercise", function()
    assert.is_not_nil(correctedId)
  end)

  it("short-circuits to the correction when asked", function()
    local v = API.GetItemVersion(correctedId, true)

    assert.is_not_nil(v)
    assert.are.equal(correctedId, v.itemId)
    assert.is_true(v.isCorrected)
    assert.are.equal(owner.major, v.expansion.major)
    assert.are.equal(0, v.minor)
    assert.are.equal(0, v.patch)
    assert.are.equal(0, v.build)
  end)

  it("ignores corrections when not asked", function()
    local v = API.GetItemVersion(correctedId, false)

    if v then
      assert.is_false(v.isCorrected)
    end
  end)
end)

describe("ItemLookup:Format", function()
  -- A real lookup, so it carries the Format method off the shared metatable.
  local function freshLookup()
    return API.GetItemVersion(presentId, false)
  end

  it("substitutes tokens with their resolved values", function()
    local lookup = freshLookup()
    local expected = string.format("v%d.%d.%d", presentRow[1], presentRow[2], presentRow[3])

    assert.are.equal(expected, lookup:Format("v{versionTriple}"))
  end)

  it("leaves a string with no tokens untouched", function()
    assert.are.equal("no tokens here", freshLookup():Format("no tokens here"))
  end)

  it("replaces every occurrence of a token", function()
    local lookup = freshLookup()
    lookup.expansion.canonName = "X"

    assert.are.equal("X-X", lookup:Format("{expacFull}-{expacFull}"))
  end)

  it("treats a percent in the replacement literally", function()
    local lookup = freshLookup()
    lookup.expansion.canonName = "100% cotton"

    assert.are.equal("100% cotton", lookup:Format("{expacFull}"))
  end)

  it("treats pattern magic in the replacement literally", function()
    local lookup = freshLookup()
    lookup.expansion.canonName = "a.b(c)[d]+"

    assert.are.equal("a.b(c)[d]+", lookup:Format("{expacFull}"))
  end)

  it("preserves pattern magic that surrounds the token in the subject", function()
    local lookup = freshLookup()
    lookup.expansion.shortName = "WW"

    assert.are.equal("(%d) WW", lookup:Format("(%d) {expacShort}"))
  end)
end)
