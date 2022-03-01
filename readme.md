# DOS Might & Magic 1 - EGA Graphics Tools

Before use, edit `common.py` and replace the contents of the `DIR` variable with your own game directory.

## To extract data

Run `python dump.py`. This will extract the wall, monster and title screen graphics for editing. The graphics all use CGA palette 0 regardless of their appearance in-game. The images are only 2bpp (they have 4 colours).

It will also create `enemies.txt` and `items.txt`, but they're just informative.

## To pack data

Run `python recombine.py`. This will produce `WALLPIX.DTA`, `MONPIX.DTA`, and ten `SCREEN#` files that can be copied into your Might & Magic directory to replace the graphics. I recommend you back up your old ones before doing this. Now you can start up the game and enjoy your handiwork.

## Future stuff

- Assign correct palettes to SCREEN files?
- Automatically fix palettes?
- Warn when source images aren't 2bpp?
- Add 4bpp support to Might & Magic and update these tools???
