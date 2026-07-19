local helper = require("helper")
local Private = helper.load()
local API = Private.API

-- Exhaustive check: the addon's binary-search lookup must agree with a plain linear
-- expansion of the runs, for every id the data covers. This is the guard that was
-- run once by hand during the run-length-encoding change and is now permanent.
describe("API.GetItemVersion against a brute-force scan of the runs", function()
  local runs = helper.reconstructRuns(Private)
  local knownMajors = helper.knownMajors(Private)

  local function expectedRow(versionId)
    local row = Private.versionIdToVersion[versionId + 1]
    if row and knownMajors[row[1]] then
      return row
    end
    -- findVersion locates the run, but GetItemVersion returns nil when the major has
    -- no expansion, so brute force must agree.
    return nil
  end

  it("matches on every covered id", function()
    local checked = 0
    local mismatches = 0
    local firstMismatch

    for _, run in ipairs(runs) do
      local row = expectedRow(run.versionId)
      for id = run.start, run.start + run.length - 1 do
        checked = checked + 1
        local got = API.GetItemVersion(id, false)

        local ok
        if row == nil then
          ok = got == nil
        else
          ok = got ~= nil
            and got.expansion.major == row[1]
            and got.minor == row[2]
            and got.patch == row[3]
            and got.build == row[4]
        end

        if not ok then
          mismatches = mismatches + 1
          firstMismatch = firstMismatch or id
        end
      end
    end

    assert.is_true(checked > 0, "expected the data to cover at least one id")
    assert.are.equal(
      0,
      mismatches,
      string.format("%d of %d covered ids mismatched (first at id %s)", mismatches, checked, tostring(firstMismatch))
    )
  end)

  it("finds nothing in the gaps between runs", function()
    local checked = 0
    local leaks = 0
    local firstLeak

    for i = 1, #runs - 1 do
      for id = runs[i].start + runs[i].length, runs[i + 1].start - 1 do
        checked = checked + 1
        if API.GetItemVersion(id, false) ~= nil then
          leaks = leaks + 1
          firstLeak = firstLeak or id
        end
      end
    end

    assert.are.equal(
      0,
      leaks,
      string.format("%d of %d gap ids resolved (first at id %s)", leaks, checked, tostring(firstLeak))
    )
  end)
end)
