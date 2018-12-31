from typing import Iterator, List, Tuple
from itertools import product
from math import sqrt, ceil
from polyominoes_types import Cell, Contour, Contours, Field, Transformation

DIAG = False
EAGER = True

if DIAG:
   generatable = [Cell(i) for i in range(6)]
else:
   generatable = [Cell.EMPTY, Cell.FULL]

# TODO: the following comments are probably outdated now that we have enums
# we use sum because diagonals have not only 0 and 1
# for squares without diagonals "if 1 in t[..." would suffice in both cases
def no_empty_rows_cols(t: Tuple[Cell, ...], H: int, W: int) -> bool:
   for row in range(H):
      if all(cell is Cell.EMPTY for cell in t[(row * W):((row + 1) * W)]):
         return False
   for col in range(W):
      if all(cell is Cell.EMPTY for cell in t[col::W]):
         return False
   return True

def connected(t: Tuple[Cell, ...], n: int, H: int, W: int) -> bool:

   t_mutable: List[int] = [cell.value for cell in t]

   def fill4(x: int, y: int) -> None:
      xy = x+W*y
      if t_mutable[xy] > 0:
         t_mutable[xy] = -t_mutable[xy]
         if y+1 < H and t_mutable[x+W*(y+1)]:
            fill4(x, y+1)
         if y > 0 and t_mutable[x+W*(y-1)]:
            fill4(x, y-1)
         if x > 0 and t_mutable[(x-1)+W*y]:
            fill4(x-1, y)
         if x+1 < W and t_mutable[(x+1)+W*y]:
            fill4(x+1, y)

   # TODO: unify with fill4
   def fill4_diag(x: int, y: int) -> None:
      xy = x+W*y
      if t_mutable[xy] > 0:
         me = t_mutable[xy]
         t_mutable[xy] = -t_mutable[xy]
         if y+1 < H:
            nb = t_mutable[x+W*(y+1)] #test neighbor
            if me in (2,4,5) and nb in (1,3,5):
               fill4_diag(x, y+1)
         if 0 < y:
            nb = t_mutable[x+W*(y-1)]
            if me in (1,3,5) and nb in (2,4,5):
               fill4_diag(x, y-1)
         if 0 < x:
            nb = t_mutable[(x-1)+W*y]
            if me in (1,4,5) and nb in (2,3,5):
               fill4_diag(x-1, y)
         if x+1 < W:
            nb = t_mutable[(x+1)+W*y]
            if me in (2,3,5) and nb in (1,4,5):
               fill4_diag(x+1, y)

   for i, c in enumerate(t):
      if c is not Cell.EMPTY:
         break

   (fill4_diag if DIAG else fill4)(i%W, i//W)

   return len([c for c in t_mutable if c < 0]) == n

def polyominoes(n: int) -> Iterator[Field]:
   """
   Numbering:
   0 1 2
   3 4 5
   6 7 8
   9 10 11

   00 10 20
   01 11 21
   02 12 22
   03 13 23
   """
   results: List[Field] = []
   for H in range(ceil(sqrt(n)), n + 1):
      for W in range(ceil(n/H), min([n + 1 - H, H]) + 1):  # W <= H and W*H >= n and W-1+H-1 <= n-1
         for t in product(generatable, repeat=H * W):
            if sum(cell is not Cell.EMPTY for cell in t) == n and no_empty_rows_cols(t, H, W) and connected(t, n, H, W):
               polyomino = [[t[x + W * y] for x in range(W)] for y in range(H)]
               # check symmetries
               # TODO: profile how much time is actually spent here checking the symmetries
               # ESPECIALLY for longer lists towards their end
               v_reflected = v_reflect(polyomino)
               if v_reflected in results:
                  continue
               h_reflected = h_reflect(polyomino)
               if h_reflected in results:
                  continue
               vh_reflected = h_reflect(v_reflected)
               if vh_reflected in results:
                  continue
               # if it is square, then additionally check rotations of every one of the four by 90
               if len(polyomino) == len(polyomino[0]):
                  if rotate(polyomino) in results:
                     continue
                  if rotate(v_reflected) in results:
                     continue
                  if rotate(h_reflected) in results:
                     continue
                  if rotate(vh_reflected) in results:
                     continue
               # finally, if we didn't find any transformation of it in our list
               results.append(polyomino)
               yield polyomino

# URGENT TODO: d seems to be identical in all three functions, but it shouldn't!
# HOW AND WHY DOES IT EVEN WORK WITH DIAGS? it is plain wrong
# TODO: after merging diags and non-diags extract duplicate code here; profile before and after
# TODO: and also extract all d-assignments because DIAG never changes during a run
# it should probably be three (or six) dicts, one (or two) for every function
def rotate(matrix: Field) -> Field:
   "rotates by 90 degrees clockwise"
   if DIAG:
      d = {Cell.EMPTY: Cell.EMPTY,
           Cell.LEFT_UPPER: Cell.RIGHT_UPPER,
           Cell.RIGHT_LOWER: Cell.LEFT_LOWER,
           Cell.RIGHT_UPPER: Cell.RIGHT_LOWER,
           Cell.LEFT_LOWER: Cell.LEFT_UPPER,
           Cell.FULL: Cell.FULL}
   else:
      d = {Cell.EMPTY: Cell.EMPTY,
           Cell.FULL: Cell.FULL}
   return [[d[elem] for elem in row[::-1]] for row in zip(*matrix)]

def v_reflect(matrix: Field) -> Field:
   "reflects across the vertical axis"
   if DIAG:
      d = {Cell.EMPTY: Cell.EMPTY,
           Cell.LEFT_UPPER: Cell.RIGHT_UPPER,
           Cell.RIGHT_LOWER: Cell.LEFT_LOWER,
           Cell.RIGHT_UPPER: Cell.RIGHT_LOWER,
           Cell.LEFT_LOWER: Cell.LEFT_UPPER,
           Cell.FULL: Cell.FULL}
   else:
      d = {Cell.EMPTY: Cell.EMPTY,
           Cell.FULL: Cell.FULL}
   return [[d[elem] for elem in row[::-1]] for row in matrix]

def h_reflect(matrix: Field) -> Field:
   "reflects across the horizontal axis"
   if DIAG:
      d = {Cell.EMPTY: Cell.EMPTY,
           Cell.LEFT_UPPER: Cell.RIGHT_UPPER,
           Cell.RIGHT_LOWER: Cell.LEFT_LOWER,
           Cell.RIGHT_UPPER: Cell.RIGHT_LOWER,
           Cell.LEFT_LOWER: Cell.LEFT_UPPER,
           Cell.FULL: Cell.FULL}
   else:
      d = {Cell.EMPTY: Cell.EMPTY,
           Cell.FULL: Cell.FULL}
   return [[d[elem] for elem in row] for row in matrix[::-1]]
