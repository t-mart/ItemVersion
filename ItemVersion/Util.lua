local _, ItemVersion = ...

ItemVersion.Util = {}

-- Mix key-value pairs from other tables (...) into object. This is commonly used to create
-- class "instances" with a particular interface.
function ItemVersion.Util.Mixin(object, ...)
  for i = 1, select("#", ...) do
    local mixin = select(i, ...)
    for k, v in pairs(mixin) do
      object[k] = v
    end
  end

  return object
end
