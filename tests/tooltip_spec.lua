-- Tooltip.lua is a client-only file, excluded from the pure-logic harness in
-- helper.lua. This spec stands up a tiny mock of the tooltip surface it touches so
-- the two behaviors that are hard to get right can be asserted out of client: the
-- dedupe guard (issue #127) and hooking the compare/shopping tooltips (issue #96).

local ADDON_NAME = "ItemVersion"
local TOOLTIP_SRC = "src/ItemVersion/Tooltip.lua"

-- A stand-in for a WoW tooltip frame. Records the lines added to it and lets a test
-- fire the render/clear scripts the way the client would.
local function newTooltip(opts)
  opts = opts or {}
  local scripts = {}
  local frame = {
    name = opts.name,
    lines = {},
    item = opts.item, -- { name = ..., link = ... }
    shown = opts.shown ~= false,
    hasSetItemScript = opts.hasSetItemScript ~= false,
  }

  function frame:HasScript(script)
    if script == "OnTooltipSetItem" then
      return self.hasSetItemScript
    end
    return script == "OnTooltipCleared"
  end

  function frame:HookScript(script, handler)
    scripts[script] = scripts[script] or {}
    table.insert(scripts[script], handler)
  end

  function frame:AddLine(text)
    table.insert(self.lines, text)
  end

  function frame:Show() end

  function frame:IsShown()
    return self.shown
  end

  function frame:GetItem()
    if self.item then
      return self.item.name, self.item.link
    end
  end

  -- Run every handler hooked to a script, the way the client does on render/clear.
  function frame:fire(script, ...)
    for _, handler in ipairs(scripts[script] or {}) do
      handler(self, ...)
    end
  end

  -- Wipe the tooltip and notify, mirroring what the client does before a refill.
  function frame:clearContents()
    for i = #self.lines, 1, -1 do
      self.lines[i] = nil
    end
    self:fire("OnTooltipCleared")
  end

  if opts.compare then
    -- A compare tooltip is filled through SetCompareItem, which clears then refills.
    -- fireSetItem models the flavors where that also emits the item render.
    function frame:SetCompareItem(link)
      self:clearContents()
      self.item = { name = "Compared", link = link }
      if opts.fireSetItem then
        self:fire("OnTooltipSetItem")
      end
    end
  end

  return frame
end

-- A Private table with just the pieces Tooltip.lua reaches into. GetItemVersion
-- returns a lookup for any id so the tooltip path always has something to add.
local function newPrivate()
  return {
    Database = {
      profile = {
        enableTooltip = true,
        showOnShift = false,
        showOnControl = false,
        showOnAlt = false,
        showOnMeta = false,
        applyCorrections = false,
        tooltipFormat = "{v}",
        lineColor = {},
      },
    },
    Color = {
      WrapTextWithColor = function(text)
        return text
      end,
    },
    API = {
      GetItemVersion = function(itemId)
        if not itemId then
          return nil
        end
        return {
          Format = function()
            return "version-" .. itemId
          end,
        }
      end,
    },
  }
end

local function stubGlobals(overrides)
  _G.IsShiftKeyDown = function()
    return false
  end
  _G.IsControlKeyDown = function()
    return false
  end
  _G.IsAltKeyDown = function()
    return false
  end
  _G.IsMetaKeyDown = function()
    return false
  end
  _G.CreateFrame = function()
    return { RegisterEvent = function() end, SetScript = function() end }
  end
  _G.hooksecurefunc = function(obj, name, post)
    local orig = obj[name]
    obj[name] = function(...)
      if orig then
        orig(...)
      end
      post(...)
    end
  end
  _G.TooltipDataProcessor = overrides.TooltipDataProcessor
  _G.Enum = overrides.Enum
end

-- Set up the mock client, load Tooltip.lua fresh (resetting its module state), and
-- hook. Returns the frames plus the Private table.
local function build(opts)
  opts = opts or {}

  local overrides = {}
  if opts.modern then
    overrides.Enum = { TooltipDataType = { Item = "Item" } }
    overrides.TooltipDataProcessor = {
      AddTooltipPostCall = function(_, callback)
        if opts.onRegister then
          opts.onRegister(callback)
        end
      end,
    }
  end
  stubGlobals(overrides)

  local hasScript = not opts.modern
  local compareOpts = function(name)
    return { name = name, hasSetItemScript = hasScript, compare = true, fireSetItem = opts.compareFiresRender }
  end

  local frames = {
    GameTooltip = newTooltip({
      name = "GameTooltip",
      hasSetItemScript = hasScript,
      item = { name = "Thing", link = "item:12345" },
    }),
    ItemRefTooltip = newTooltip({ name = "ItemRefTooltip", hasSetItemScript = hasScript }),
    ShoppingTooltip1 = newTooltip(compareOpts("ShoppingTooltip1")),
    ShoppingTooltip2 = newTooltip(compareOpts("ShoppingTooltip2")),
    ItemRefShoppingTooltip1 = newTooltip(compareOpts("ItemRefShoppingTooltip1")),
    ItemRefShoppingTooltip2 = newTooltip(compareOpts("ItemRefShoppingTooltip2")),
  }

  _G.GameTooltip = frames.GameTooltip
  _G.ItemRefTooltip = frames.ItemRefTooltip
  _G.ShoppingTooltip1 = frames.ShoppingTooltip1
  _G.ShoppingTooltip2 = frames.ShoppingTooltip2
  _G.ItemRefShoppingTooltip1 = frames.ItemRefShoppingTooltip1
  _G.ItemRefShoppingTooltip2 = frames.ItemRefShoppingTooltip2

  local Private = newPrivate()
  assert(loadfile(TOOLTIP_SRC))(ADDON_NAME, Private)
  Private.Tooltip.HookTooltip()

  frames.Private = Private
  return frames
end

local function versionLineCount(frame)
  local count = 0
  for _, line in ipairs(frame.lines) do
    if type(line) == "string" and line:find("version-", 1, true) then
      count = count + 1
    end
  end
  return count
end

describe("Tooltip", function()
  describe("dedupe guard", function()
    it("adds the version line only once when the render fires twice for one fill", function()
      local ctx = build()
      ctx.GameTooltip:fire("OnTooltipSetItem")
      ctx.GameTooltip:fire("OnTooltipSetItem")
      assert.are.equal(1, versionLineCount(ctx.GameTooltip))
    end)

    it("adds the line again after the tooltip is cleared", function()
      local ctx = build()
      ctx.GameTooltip:fire("OnTooltipSetItem")
      ctx.GameTooltip:clearContents()
      ctx.GameTooltip:fire("OnTooltipSetItem")
      assert.are.equal(1, versionLineCount(ctx.GameTooltip))
    end)
  end)

  describe("compare tooltips", function()
    it("annotates a compare tooltip through the render hook", function()
      local ctx = build()
      ctx.ShoppingTooltip1.item = { name = "Ring", link = "item:777" }
      ctx.ShoppingTooltip1:fire("OnTooltipSetItem")
      assert.are.equal(1, versionLineCount(ctx.ShoppingTooltip1))
    end)

    it("annotates a compare tooltip filled via SetCompareItem with no render", function()
      local ctx = build({ compareFiresRender = false })
      ctx.ShoppingTooltip1:SetCompareItem("item:777")
      assert.are.equal(1, versionLineCount(ctx.ShoppingTooltip1))
    end)

    it("does not double the line when SetCompareItem also emits a render", function()
      local ctx = build({ compareFiresRender = true })
      ctx.ShoppingTooltip1:SetCompareItem("item:777")
      assert.are.equal(1, versionLineCount(ctx.ShoppingTooltip1))
    end)
  end)

  describe("data-processor path", function()
    it("annotates hooked frames and ignores frames it does not hook", function()
      local callback
      local ctx = build({
        modern = true,
        onRegister = function(cb)
          callback = cb
        end,
      })

      callback(ctx.GameTooltip, { id = 12345 })
      assert.are.equal(1, versionLineCount(ctx.GameTooltip))

      local stranger = newTooltip({ name = "SomeOtherTooltip", hasSetItemScript = false })
      callback(stranger, { id = 12345 })
      assert.are.equal(0, versionLineCount(stranger))
    end)
  end)
end)
