from typing import List, Optional, Tuple
from polyominoes_types import Cell, Contour, Contours, Field
from field_to_contours import fill, get_dims, inversions

def find_zeroth_vertex(field: Field) -> Optional[Tuple[int, int]]:
   # currently: find the leftmost of the uppermost filled cells
   for i, row in enumerate(field):
      for j, cell in enumerate(row):
         if cell is not Cell.EMPTY:
            quadruple = get_quadruple(field, i, j)
            normalize_quadruple(quadruple)
            if quadruple != [0,0,0,0]: # TODO: add other illegal starting points
               print("START AT", quadruple)
               return j, i
   return None

def get_quadruple(field: Field, i: int, j: int) -> List[Cell]:
   nrows, ncols = get_dims(field)
   return [field[i - 1][j - 1].value if i > 0 and j > 0 else Cell.EMPTY,
           field[i - 1][j].value if i > 0 and j < ncols else Cell.EMPTY,
           field[i][j - 1].value if i < nrows and j > 0 else Cell.EMPTY,
           field[i][j].value if i < nrows and j < ncols else Cell.EMPTY]

def normalize_quadruple(quadruple: List[Cell]) -> None:
   """THIS FUNCTION MUTATES ITS ARGUMENT"""
   # Validate quadruple, just in case:
   if len(quadruple) != 4:
      raise ValueError(f"Invalid quadruple {quadruple}")
   # There are 6^4 = 1296 possible quadruples to consider (although some of them, like 0000 or 5555, should never happen)
   # it would not be wise to list all of them as we did in older redactor versions, without diagonals
   # So we do it a bit differently:
   if quadruple[0] == Cell.LEFT_UPPER.value:
      quadruple[0] = Cell.EMPTY.value
   elif quadruple[0] == Cell.RIGHT_LOWER.value:
      quadruple[0] = Cell.FULL.value
   if quadruple[1] == Cell.RIGHT_UPPER.value:
      quadruple[1] = Cell.EMPTY.value
   elif quadruple[1] == Cell.LEFT_LOWER.value:
      quadruple[1] = Cell.FULL.value
   if quadruple[2] == Cell.RIGHT_UPPER.value:
      quadruple[2] = Cell.FULL.value
   elif quadruple[2] == Cell.LEFT_LOWER.value:
      quadruple[2] = Cell.EMPTY.value
   if quadruple[3] == Cell.LEFT_UPPER.value:
      quadruple[3] = Cell.FULL.value
   elif quadruple[3] == Cell.RIGHT_LOWER.value:
      quadruple[3] = Cell.EMPTY.value
   # now only 256 possible quadruples remain (and some of them should never happen)

def field_to_contours(field: Field) -> Contours:
   field = [[Cell.FULL if i in (Cell.LEFT_UPPER_RIGHT_LOWER, Cell.RIGHT_UPPER_LEFT_LOWER) else i for i in row] for row in field] # coercing full cells cut in two halfs to uncut full cells
   # TODO: check if connected
   
   # adding an empty top row, an empty bottom row, an empty right column and an empty left column
   # this is done to make sure the outer empty part (without the holes) is contiguous
   nrows, ncols = get_dims(field)
   field = [[Cell.EMPTY] * (ncols+2)] + [[Cell.EMPTY] + row + [Cell.EMPTY] for row in field] + [[Cell.EMPTY] * (ncols+2)]

   # inner function to get one of the contours
   def field_to_one_contour(field: Field) -> Contour:
      ji = find_zeroth_vertex(field)
      if ji is None:
         raise ValueError("Can't find zeroth vertex, this is a bug")
      j, i = ji
      contour = [(j,i)]
      
      while True:
         quadruple = get_quadruple(field, i, j)
         normalize_quadruple(quadruple)
         if quadruple in ([0,0,0,4], [0,0,0,5], [0,2,0,5], [0,5,0,5], [3,5,0,5], [5,5,0,5], [5,5,1,5]):
            i += 1
            """
            .. .# ##
            .# .# .#
            """
         elif quadruple in ([0,0,1,0], [0,0,5,0], [0,0,5,4], [0,0,5,5], [0,2,5,5], [0,5,5,5], [3,5,5,5]):
            j -= 1
            """
            .. .. .#
            #. ## ##
            """
         elif quadruple in ([0,2,0,0], [0,5,0,0], [3,5,0,0], [5,5,0,0], [5,5,1,0], [5,5,5,0], [5,5,5,4]):
            j += 1
            """
            .# ## ##
            .. .. #.
            """
         elif quadruple in ([3,0,0,0], [5,0,0,0], [5,0,1,0], [5,0,5,0], [5,0,5,4], [5,0,5,5], [5,2,5,5]):
            i -= 1
            """
            #. #. #.
            .. #. ##
            """
         elif quadruple in ([0,1,0,0], [3,1,0,0], [5,1,0,0], [5,1,1,0], [5,1,5,0], [5,1,5,4], [5,1,5,5]):
            i -= 1
            j += 1
            """
            #/
            ##
            """
         elif quadruple in ([4,0,0,0], [4,0,1,0], [4,0,5,0], [4,0,5,4], [4,0,5,5], [4,2,5,5], [4,5,5,5]):
            i -= 1
            j -= 1
            """
            \#
            ##
            """
         elif quadruple in ([0,0,2,0], [0,0,2,4], [0,0,2,5], [0,2,2,5], [0,5,2,5], [3,5,2,5], [5,5,2,5]):
            i += 1
            j -= 1
            """
            ##
            /#
            """
         elif quadruple in ([0,0,0,3], [0,2,0,3], [0,5,0,3], [3,5,0,3], [5,5,0,3], [5,5,1,3], [5,5,5,3]):
            i += 1
            j += 1
            """
            ##
            #\
            """
         elif quadruple == [0, 5, 5, 0]:
            if contour[-2][0] != contour[-1][0]:  # j-coord
               raise RuntimeError("why?")
            if contour[-1][1] > contour[-2][1]:
               j += 1
            elif contour[-1][1] < contour[-2][1]:
               j -= 1
            else:
               raise RuntimeError("why?")
            """
            .#
            #.
            """
         elif quadruple == [5, 0, 0, 5]:
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
