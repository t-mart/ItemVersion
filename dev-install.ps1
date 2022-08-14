# Make a junction (like a symlink) from this repository's source directory to the WoW addons directory
# This way, you don't have to copy files back and forth
New-Item -ItemType Junction -Path "C:\Program Files (x86)\World of Warcraft\_retail_\Interface\AddOns\ItemVersion" -Value "ItemVersion"
