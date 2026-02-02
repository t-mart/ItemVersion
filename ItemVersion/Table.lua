local _, Private = ...

---Creates a deep copy of a table
---Note: Does not handle cyclic references
---@generic T
---@param obj T The object to copy
---@return T copy The deep copy of the object
local function deepCopy(obj)
  -- Does not handle cyclic references
  if type(obj) ~= 'table' then return obj end

  local res = {}
  for k, v in pairs(obj) do
    -- Recursively copy the key and the value
    res[deepCopy(k)] = deepCopy(v)
  end

  return res
end

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
  DeepCopy = deepCopy,
  Mixin = mixin,
  KeepOnlyKnownKeys = keepOnlyKnownKeys,
}
