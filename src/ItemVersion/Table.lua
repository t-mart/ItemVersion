local _, Private = ...

---Mixes in properties from one or more mixin tables into a target object
---@generic T
---@param object T The target object to receive the mixin properties
---@param ... table One or more mixin tables
---@return T object The modified object with mixin properties
local function mixin(object, ...)
  for i = 1, select("#", ...) do
    local source = select(i, ...) -- Renamed 'mixin' to 'source'
    for k, v in pairs(source) do
      object[k] = v
    end
  end

  return object
end

---Removes all keys from a table that are not present in the allowed table
---@param t table The table to clean
---@param allowed table A table containing the allowed keys
local function keepOnlyKnownKeys(t, allowed)
  for k, _ in pairs(t) do
    if allowed[k] == nil then
      t[k] = nil
    end
  end
end

Private.Table = {
  Mixin = mixin,
  KeepOnlyKnownKeys = keepOnlyKnownKeys,
}
