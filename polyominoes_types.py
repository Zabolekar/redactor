from typing import Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

class Cell(Enum):
   """
   0 1 2 3 4 5 can be generated directly,
   6 7 can only appear when multiple figures are combined
   """
   EMPTY = 0 # __
   LEFT_UPPER = 1 # |/
   RIGHT_LOWER = 2 # /|
   RIGHT_UPPER = 3 # \|
   LEFT_LOWER = 4 # |\
   FULL = 5 # |_|
   LEFT_UPPER_RIGHT_LOWER = 6 # |/|
   RIGHT_UPPER_LEFT_LOWER = 7 # |\|

   def __bool__(self) -> bool:
      raise TypeError("To find out if a cell is empty compare it with Cell.EMPTY explicitly")

   def __eq__(self, other: Any) -> bool:
      if isinstance(other, Cell):
         return super().__eq__(other)
      else:
         raise TypeError("Please only compare cells to other cells")

   def __ne__(self, other: Any) -> bool:
      if isinstance(other, Cell):
         return super().__ne__(other)
      else:
         raise TypeError("Please only compare cells to other cells")

   def __hash__(self) -> int:
      return super().__hash__()

# type aliases
Vertex = Tuple[int, int]
Contour = List[Vertex]
Contours = List[Contour]
Row = List[Cell]
Field = List[Row]

@dataclass
class Hmm: # TODO: better name; what's its meaning?
   x: int
   y: int
   cell: Cell = Cell.EMPTY # this field is rarely used, only for diagonals

class Transformation(Enum):
   UP = 1
   DOWN = 2
   LEFT = 3
   RIGHT = 4
   ROTATE = 5
   REFLECT_OVER_VERTICAL_AXIS = 6
   REFLECT_OVER_HORIZONTAL_AXIS = 7

   def __init__(self, value: int) -> None:
      self.is_translation = self.name in ["UP", "DOWN", "LEFT", "RIGHT"]
      if self.is_translation:
         self.dx = {1: 0, 2: 0, 3: -1, 4: 1}[value]
         self.dy = {1: -1, 2: 1, 3: 0, 4: 0}[value]
