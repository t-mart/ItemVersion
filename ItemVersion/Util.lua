local _, ItemVersion = ...

ItemVersion.Util = {}

function ItemVersion.Util.WrapTextInColor(text, color)
  local hex = ("ff%.2x%.2x%.2x"):format(Round(color.r * 255), Round(color.g * 255), Round(color.b * 255));
  return WrapTextInColorCode(text, hex);
end
