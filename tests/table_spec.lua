local Private = require("helper").load()
local Table = Private.Table

describe("Table.Mixin", function()
  it("copies properties from a source onto the object", function()
    local object = { a = 1 }
    local result = Table.Mixin(object, { b = 2, c = 3 })

    assert.are.equal(object, result)
    assert.are.same({ a = 1, b = 2, c = 3 }, object)
  end)

  it("applies sources left to right, so later ones win", function()
    local object = Table.Mixin({}, { x = 1 }, { x = 2 })

    assert.are.equal(2, object.x)
  end)

  it("returns the object when there are no sources", function()
    local object = { a = 1 }

    assert.are.equal(object, Table.Mixin(object))
  end)
end)

describe("Table.KeepOnlyKnownKeys", function()
  it("drops keys absent from the allowed set", function()
    local t = { keep = 1, drop = 2 }

    Table.KeepOnlyKnownKeys(t, { keep = true })

    assert.are.same({ keep = 1 }, t)
  end)

  it("keeps an allowed key even when its value is falsy", function()
    local t = { off = false }

    Table.KeepOnlyKnownKeys(t, { off = true })

    assert.are.same({ off = false }, t)
  end)

  it("leaves the table empty when nothing is allowed", function()
    local t = { a = 1, b = 2 }

    Table.KeepOnlyKnownKeys(t, {})

    assert.are.same({}, t)
  end)
end)
