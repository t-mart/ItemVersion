local Private = require("helper").load()
local Color = Private.Color

describe("Color.ToHexString", function()
  it("formats white as fully opaque white", function()
    assert.are.equal("FFFFFFFF", Color.ToHexString(Color.White()))
  end)

  it("defaults a missing alpha to fully opaque", function()
    assert.are.equal("FF000000", Color.ToHexString({ r = 0, g = 0, b = 0 }))
  end)

  it("honors an explicit alpha", function()
    assert.are.equal("00000000", Color.ToHexString({ r = 0, g = 0, b = 0, a = 0 }))
  end)

  it("orders the channels as AARRGGBB", function()
    assert.are.equal("FFFF0000", Color.ToHexString({ r = 1, g = 0, b = 0 }))
    assert.are.equal("FF00FF00", Color.ToHexString({ r = 0, g = 1, b = 0 }))
    assert.are.equal("FF0000FF", Color.ToHexString({ r = 0, g = 0, b = 1 }))
  end)

  it("floors fractional channels", function()
    -- 0.5 * 255 = 127.5 -> 127 -> 0x7F
    assert.are.equal("FF7F7F7F", Color.ToHexString({ r = 0.5, g = 0.5, b = 0.5 }))
  end)
end)

describe("Color.WrapTextWithColor", function()
  it("wraps text in a color escape and a reset", function()
    local wrapped = Color.WrapTextWithColor("hi", Color.White())

    assert.are.equal("|cFFFFFFFF" .. "hi" .. "|r", wrapped)
  end)
end)
