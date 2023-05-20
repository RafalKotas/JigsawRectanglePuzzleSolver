# JigsawRectanglePuzzleSolver
Rectange Jigsaw Puzzle Solver using MSE mosaic tile matching

Description:
A simple application for instructing how to solve rectangular puzzles in the least number of moves.
It was created as a result of the need to solve a mosaic puzzle based on an original picture.
The method matches parts of an image to a mosaic puzzle based on a minimum MSE (Mean Squared Error).

#### Usage:
1. Puzzle names are marked with numbers so if you want to add your new puzzle:
- you need to create a folder with a specific number
- create file with the mosaic ("<puzzle_no>_mosaic.png")
- create file with the original image ("<puzzle_no>.png")
2. Define maximum allowed moves count in *moves_to_beat*, the solution instruction will be displayed only 
when the calculated minimum number of moves (< puzzleMosaicWidth * puzzleMosaicHeight) is less than the value of this variable

Note(s):
- files with name like "<puzzle_no>-mosaic-nc.png" are screenshots from a webpage (***pazyl.pl***) containing puzzles involving, among others, solving puzzles
