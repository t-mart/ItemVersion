# Translation Effort

Do you know another language and want to help this project?

If so, I'd really appreciate your help. Here's what you need to do:

1. If not done already, create the new locale file and add it for loading. _If this has already been
   done, continue to step #2._

   1. Copy `enUS.lua` to a new file named for the locale that you can translate. See the locale
      codes below.

   2. Change this line

      ```diff
      - local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "enUS", true)
      + local L = LibStub("AceLocale-3.0"):NewLocale(addonName, "xxYY")
      ```

      (Replace `xxYY` with your locale code, such as frFR, deDE, etc. And, also note that we have
      removed the third parameter.)

   3. Add the file to `locales.xml`.

      ```xml
      <Include file="Locales\xxYY.lua" />
      ```

      (Replace `xxYY` with your locale code here too.)

2. Translate the strings:

   ```lua
   L["Tooltip"] = "Your translation of `Tooltip` goes here."
   L["..."] = "..."
   ```

   Or, if the text used in English is sufficient in the target language, set it to `true`:

   ```lua
   L["No change needed"] = true
   ```

3. Submit a pull request to the project.
