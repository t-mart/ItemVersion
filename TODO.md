- Fix options. Yeesh, this sucks.
  - lots of pro examples at https://www.townlong-yak.com/framexml/live
  - Create a new widget for editing the tooltip format string.
  - Preview widget that shows icons so user can hover and see what tooltip looks
    like.
- Add slash commands
  - /iv to open options
  - /iv <itemlink | itemId> <boolean?> to lookup an item, boolean if corrections
    are applied
- Revisit locales. I think I'm doing it wrong.
- Revist tooltip hooking. I think I'm doing it wrong. See
  https://www.townlong-yak.com/framexml/beta/Blizzard_GameTooltip/GameTooltip.lua
  (also check classic builds for differences)
- Ensure only present strings are in locales. We've got some old ones for sure.
  Do this for non-English locales too.
- Format Code Description Example {expacLong} The long name of the expansion
  Mists of Pandaria {expacShort} The short name of the expansion MoP {version}
  The dot-separated version 5.0.1 {build} The build number 15640
- use https://warcraft.wiki.gg/wiki/API_C_Item.GetItemInfo as fallback if lookup
  fails?
- test on all clients (might need to resub)
- add icons to tooltip is possible? https://warcraft.wiki.gg/wiki/UIHANDLER_OnTooltipSetItem