# Locales

This folder contains translation files. Each string in used in the addon can be
translated into multiple languages. The files are named according to the locale
they represent, e.g., `enUS.lua` for U.S. English, `deDE.lua` for German, etc.

The format of each file should look like this:

```lua
local AddonName = ...

local L = LibStub("AceLocale-3.0"):NewLocale(AddonName, "deDE")
if not L then return end

-- L["<english string>"] = "<translated string>"
L["string1"] = "Zeichenkette1"
-- and so on
```

The strings to translate should be the ones found in `enUS.lua`. If a string is
not translated, the English version will be used as a fallback.

See <https://www.wowace.com/projects/ace3/pages/api/ace-locale-3-0> for more
details.
