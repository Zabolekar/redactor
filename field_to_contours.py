from typing import List, Tuple
from enum import Enum
from polyominoes_types import Cell, Field, Contour, Contours

inversions = { # this already is ok for use with diagonals
   Cell.EMPTY: Cell.FULL,
   Cell.LEFT_UPPER: Cell.RIGHT_LOWER,
   Cell.RIGHT_LOWER: Cell.LEFT_UPPER,
   Cell.RIGHT_UPPER: Cell.LEFT_LOWER,
   Cell.LEFT_LOWER: Cell.RIGHT_UPPER,
   Cell.FULL: Cell.EMPTY
} # only used in field_to_contours

def get_dims(field: Field) -> Tuple[int, int]:
   nrows, ncols = len(field), len(field[0])
   return nrows, ncols

class Status(Enum):
   CHECKED = 0
   TO_BE_CHECKED = 1
   BEING_CHECKED = 2
   UNCHECKED = 3

def fill(field: Field, y: int, x: int, new_value: Cell) -> Field:
   nrows, ncols = get_dims(field)
   old_value = field[y][x]
   auxiliary_field: List[List[Status]] = [[Status.UNCHECKED for __ in row] for row in field]
   auxiliary_field[y][x] = Status.BEING_CHECKED
   while sum(Status.BEING_CHECKED in row for row in auxiliary_field):
      for y in range(nrows):
         for x in range(ncols):
            if auxiliary_field[y][x] == Status.BEING_CHECKED:
               neighbours = []
               # regular neighbours
               if y > 0:
                  neighbours.append((y - 1, x))
               if y + 1 < nrows:
                  neighbours.append((y + 1, x))
               if x > 0:
                  neighbours.append((y, x - 1))
               if x + 1 < ncols:
                  neighbours.append((y, x + 1))
               for ny, nx in neighbours:
                  if auxiliary_field[ny][nx] == Status.UNCHECKED and field[ny][nx] == old_value:
                     auxiliary_field[ny][nx] = Status.TO_BE_CHECKED
               auxiliary_field[y][x] = Status.CHECKED
      for y in range(nrows):
         for x in range(ncols):
            if auxiliary_field[y][x] == Status.TO_BE_CHECKED:
               auxiliary_field[y][x] = Status.BEING_CHECKED
   result = [row[:] for row in field]  # copying
   # actually filling:
   for y in range(nrows):
      for x in range(ncols):
         if auxiliary_field[y][x] == Status.CHECKED:
            result[y][x] = new_value
   return result

def field_to_contours(field: Field) -> Contours:
   # TODO: check if connected

   # adding an empty top row, an empty bottom row, an empty right column and an empty left column
   # this is done to make sure the outer empty part (without the holes) is contiguous
   nrows, ncols = len(field) + 2, len(field[0]) + 2
   field = [[Cell.EMPTY] * ncols] + [[Cell.EMPTY] + row + [Cell.EMPTY] for row in field] + [[Cell.EMPTY] * ncols]

   # inner function to get one of the contours
   def field_to_one_contour(field: Field) -> Contour:
      # find the leftmost of the uppermost filled cells
      # TODO: rethink the algorithm
      break_flag = False
      for i, row in enumerate(field):
         for j, cell in enumerate(row):
            if cell is not Cell.EMPTY:
               break_flag = True
               break
         if break_flag:
            break
      contour = [(j, i)]

      while True:
         quadruple = (field[i - 1][j - 1].value if i > 0 and j > 0 else 0,
                      field[i - 1][j].value if i > 0 and j < ncols else 0,
                      field[i][j - 1].value if i < nrows and j > 0 else 0,
                      field[i][j].value if i < nrows and j < ncols else 0)
         if quadruple == (0, 0, 0, 0):
            raise RuntimeError("Something unexpected happened")
            """
            ..
            ..
            """
         elif quadruple == (0, 0, 0, 5):
            i += 1
            """
            ..
            .#
            """
         elif quadruple == (0, 0, 5, 0):
            j -= 1
            """
            ..
            #.
            """
         elif quadruple == (0, 0, 5, 5):
            j -= 1
            """
            ..
            ##
            """
         elif quadruple == (0, 5, 0, 0):
            j += 1
            """
            .#
            ..
            """
         elif quadruple == (0, 5, 0, 5):
            i += 1
            """
            .#
            .#
            """
         elif quadruple == (0, 5, 5, 0):
            if contour[-2][0] != contour[-1][0]:  # j-coord
               raise RuntimeError("why?")
            if contour[-1][1] > contour[-2][1]:
               j += 1
            elif contour[-1][1] < contour[-2][1]:
               j -= 1
            else:
               raise RuntimeError("honestly, why?")
            """
            .#
            #.
            """
         elif quadruple == (0, 5, 5, 5):
            j -= 1
            """
            .#
            ##
            """
         elif quadruple == (5, 0, 0, 0):
            i -= 1
            """
            #.
            ..
            """
         elif quadruple == (5, 0, 0, 5):
            if contour[-1][1] != contour[-2][1]:  # i-coord
               raise RuntimeError("how?")
            if contour[-1][0] > contour[-2][0]:
               i -= 1
            elif contour[-1][0] < contour[-2][0]:
               i += 1
            else:
               raise RuntimeError("honestly, how?")
            """
            #.
            .#
            """
         elif quadruple == (5, 0, 5, 0):
            i -= 1
            """
            #.
            #.
            """
         elif quadruple == (5, 0, 5, 5):
            i -= 1
            """
            #.
            ##
            """
         elif quadruple == (5, 5, 0, 0):
            j += 1
            """
            ##
            ..
            """
         elif quadruple == (5, 5, 0, 5):
            i += 1
            """
            ##
            .#
            """
         elif quadruple == (5, 5, 5, 0):
            j += 1
            """
            ##
            #.
            """
         elif quadruple == (5, 5, 5, 5):
            raise RuntimeError(f"Something unexpected happened, quadruple is {quadruple}")
            """
            ##
            ##
            """
         else:
            raise RuntimeError(f"Something unexpected happened, quadruple is {quadruple}")
         contour.append((j, i))
         if contour[-1] == contour[0]:
            break
      return contour

   outer = field_to_one_contour(field)
   # calculate some kind of center
   meanX = round(sum(x for x, y in outer) / len(outer))
   meanY = round(sum(y for x, y in outer) / len(outer))

   contours = [outer]

   # fill the outer blank space, then invert
   holes_inverted = [[inversions[cell] for cell in row] for row in fill(field, 0, 0, Cell.FULL)]

   # actually find the holes and add them (reversed) to contours
   while any(cell is not Cell.EMPTY for row in holes_inverted for cell in row):
      contour = field_to_one_contour(holes_inverted)
      j, i = contour[0]
      holes_inverted = fill(holes_inverted, i, j, Cell.EMPTY)
      contours.append(list(reversed(contour)))

   centered = [[(x - meanX, y - meanY) for x, y in contour] for contour in contours]
   return centered
