# Item Version Context

Item Version is a World of Warcraft addon that displays item version information
in tooltips. When players hover over items or click item links, the addon adds a
line to the tooltip indicating the expansion and version in which the item was
introduced to the game.

The addon allows users to customize how this information is presented through
various options, including color settings, key modifiers, and tooltip format
strings.

The addon also supports localization for different languages.

The game supports as many flavors (versions) of the game as possible. Notably,
not all APIs are available in all versions. This addon is primarily developed
and tested on the Retail version of World of Warcraft, but we strive to work on
Classic versions as well.

## Implementation

We provide a data table in Data.lua. That comes from an external process to this
project.

In game, we hook into the item tooltip rendering process. When an item tooltip
is shown, we look up the item ID in our database, format the version information
according to user settings, and inject that line into the tooltip.

### Options

Options are almost the most difficult part of this project because we need to
start caring about user experience and interface design.

We use Ace3 wherever possible, but sometimes we need to step down to native WoW
APIs for certain functionality.

In particular, the options screen is built using Ace, but because Ace only
offers a limited set of widgets, we sometimes need to create our own custom
widgets.

## Key Directories

- `ItemVersion/`: Main addon code.
- `ItemVersion/Locales/`: Localization files for different languages.
- `ItemVersion/Libs/`: Library files, primarily for Ace3 framework. This is a
  gold mine for seeing how Ace3 works under the hood. It's sometimes more
  helpful than the Ace3 docs.
- `docs/frame-xml-reference/`: Reference files from the game's FrameXML for
  different flavors of WoW, authored by Blizzard themselves. These are
  implemented in .xml and .lua files. This code drives all the interfaces in the
  respective flavors that we care about.
  - **Retail**: `frame-xml-reference/_retail_ 12.0.0.65655/` (Currently in
    Mightnight progress)
  - **Classic**: `frame-xml-reference/_classic_ 5.5.3.64857/` (Currently in
    Mists of Pandaria progress)
  - **Classic Era**: `frame-xml-reference/_classic_era_ 1.15.8.64907` (Currently
    in Vanilla 1.15.8 progress)
  - **Anniversary**: `frame-xml-reference/_anniversary_ 2.5.5.65534/` (Currently
    in Burning Crusade progress)

  We should look at various APIs in these flavors to ensure compatibility where
  possible.

  In particular, look how tooltips work, look how Settings/Options work, and
  look how frames are constructed.

  It's also a great reference for WoW UI programming in general. It's especially
  good for seeing how the native Blizzard UIs are built. (Note that UIs can also
  be written in XML, but we don't do that in this project. The XML is mappable
  to Lua.)

- `docs/ace3/`: Ace3 library documentation for reference. This is a wget dump of
  the documentation site. Ace3 isn't official, but it provides a lot of useful
  functionality for WoW addon development. We try to use is where we can, but it
  does have its limitations.

  If I ever ask about Ace3, this is where I go to look for answers.

## Key Files

- `TODO.md`: List of tasks and features to implement.
- `README.md`: Overview and documentation for the addon.
- `docs/API.md`: Documentation for the addon's API.
- `ItemVersion/API.lua`: Implementation of the addon's API.
- `ItemVersion/Options.lua`: Implementation of the addon's options and settings.
- `ItemVersion/Tooltip.lua`: Implementation of tooltip modifications. This is a
  work in progres, still needs overhaul.
- `ItemVersion/Data.lua`: This is a massive file containing the item version
  database. It should not be extensively read through... It's just tables with
  item IDs and version info. See the API.lua for the interface that's more
  relevant.
- `ItemVersion/Expansion.lua`: Source code data representing expansions and
  version corrections.

## Project State

This project is undergoing an overhaul to improve code quality. But it is a work
in progress and not in a releasable state. Inconsistencies may exist until the
overhaul is complete.
