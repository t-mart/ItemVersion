local _, Private = ...


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


Private.Util = {
  DeepCopy = deepCopy,
}
