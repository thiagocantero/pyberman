# Introduction #

Pyberman's levels are stored in external files, so new levels can be introduced by users. Files resist in 'maps' subfolder of the main distribution folder. You can add new files and they will become available in the interface.

# Details #

The extension of a specific map file is .bff - which means bomberman field file. Internally, those are simple text files, so feel free to edit them with your favorite text editor (notepad?).

First line of the file consists of 3 numbers: height, width of the field and maximum amount of players that can play on this map.

The next height lines consist of corresponding chars:
  * 'W' stands for wall
  * 'B' stands for box
  * ' ' stands for grass (empty space)
  * 'S' stand for start positions of players correspondingly. Make sure that number of start positions correspond to those specified in the first line of the file.

# Example #
```
13 17 2
WWWWWWWWWWWWWWWWW
W  BBBBBBBBBBBBBW
WSWBWBWBWBWBWBWBW
WBBBBBBBBBBBBBBBW
WBWBWBWBWBWBWBWBW
WBBBBBBBBBBBBBBBW
WBWBWBWBWBWBWBWBW
WBBBBBBBBBBBBBBBW
WBWBWBWBWBWBWBWBW
WBBBBBBBBBBBBBBBW
WBWBWBWBWBWBWBWSW
WBBBBBBBBBBBBB  W
WWWWWWWWWWWWWWWWW
```