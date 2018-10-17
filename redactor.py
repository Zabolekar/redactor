from tkinter import Tk, Toplevel, Canvas, Label, Spinbox, Button, IntVar, Event, filedialog, messagebox
from typing import Any, List, Tuple, Iterator, Callable, Dict, Optional, Union
from dataclasses import dataclass
from itertools import product
from math import sqrt, ceil
from copy import deepcopy
from warnings import warn
from io import StringIO
from enum import Enum

DIAG = False
EAGER = True

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

if DIAG:
   generatable = [Cell(i) for i in range(6)]
else:
   generatable = [Cell.EMPTY, Cell.FULL]

inversions = {
   Cell.EMPTY: Cell.FULL,
   Cell.LEFT_UPPER: Cell.RIGHT_LOWER,
   Cell.RIGHT_LOWER: Cell.LEFT_UPPER,
   Cell.RIGHT_UPPER: Cell.LEFT_LOWER,
   Cell.LEFT_LOWER: Cell.RIGHT_UPPER,
   Cell.FULL: Cell.EMPTY
} # only used in field_to_contours

# type aliases
Vertex = Tuple[int, int]
Contour = List[Vertex]
Contours = List[Contour]
Row = List[Cell]
Field = List[Row]
Callback = Callable[[Event], None]

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
            if sum(map(lambda cell: cell is not Cell.EMPTY, t)) == n and no_empty_rows_cols(t, H, W) and connected(t, n, H, W):
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

######################################################
##### Neither generation-related nor GUI-related #####
######################################################

def print_field(field: Field) -> None:
   # cutting empty rows
   for i, row in enumerate(field):
      if sum(row):
         break
   for j, row in reversed(list(enumerate(field, 1))):
      if sum(row):
         break
   # TODO: cut empty columns, too
   print("\n".join("".join('#' if cell else ' ' for cell in row) for row in field[i:j]))
   print("\n\n")

def fill(field: Field, y: int, x: int, new_value: Cell) -> Field:
   nrows, ncols = get_dims(field)
   old_value = field[y][x]
   auxiliary_field = [['unchecked' for __ in row] for row in field]
   # auxiliary_field cell can have four distinct values:
   # unchecked; about to be checked; being checked now; checked;
   auxiliary_field[y][x] = 'being checked'
   while sum('being checked' in row for row in auxiliary_field):
      for y in range(nrows):
         for x in range(ncols):
            if auxiliary_field[y][x] == 'being checked':
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
               # diagonal neighbours
               if y > 0 and x > 0:
                  neighbours.append((y - 1, x - 1))
               if y + 1 < nrows and x > 0:
                  neighbours.append((y + 1, x - 1))
               if y > 0 and x + 1 < ncols:
                  neighbours.append((y - 1, x + 1))
               if y + 1 < nrows and x + 1 < ncols:
                  neighbours.append((y + 1, x + 1))
               for ny, nx in neighbours:
                  if auxiliary_field[ny][nx] == 'unchecked' and field[ny][nx] == old_value:
                     auxiliary_field[ny][nx] = 'to be checked'
               auxiliary_field[y][x] = 'checked'
      for y in range(nrows):
         for x in range(ncols):
            if auxiliary_field[y][x] == 'to be checked':
               auxiliary_field[y][x] = 'being checked'
   result = [row[:] for row in field]  # copying
   # actually filling:
   for y in range(nrows):
      for x in range(ncols):
         if auxiliary_field[y][x] == 'checked':
            result[y][x] = new_value
   return result
   
def get_dims(field: Field) -> Tuple[int, int]:
   nrows, ncols = len(field), len(field[0])
   return nrows, ncols

def field_to_contours(field: Field) -> Contours:
   # TODO: check if connected

   # adding an empty top row, an empty bottom row, an empty right column and an empty left column
   # this is done to make sure the outer empty part (without the holes) is contiguous
   nrows, ncols = len(field) + 2, len(field[0]) + 2
   field = [[Cell.EMPTY] * ncols] + [[Cell.EMPTY] + row + [Cell.EMPTY] for row in field] + [[Cell.EMPTY] * ncols]

   # inner function to get one of the contours
   def field_to_one_contour(field: Field) -> Contour:
      # find the leftmost of the uppermost filled cells
      break_flag = False
      for i, row in enumerate(field):
         if sum(row):
            for j, cell in enumerate(row):
               if cell is not Cell.EMPTY:
                  break_flag = True
                  break
         if break_flag:
            break
      contour = [(j, i)]

      while True:
         quadruple = (field[i - 1][j - 1] if i > 0 and j > 0 else 0,
                      field[i - 1][j] if i > 0 and j < ncols else 0,
                      field[i][j - 1] if i < nrows and j > 0 else 0,
                      field[i][j] if i < nrows and j < ncols else 0)
         if quadruple == (0, 0, 0, 0):
            raise RuntimeError("Something unexpected happened")
            """
            ..
            ..
            """
         elif quadruple == (0, 0, 0, 1):
            i += 1
            """
            ..
            .#
            """
         elif quadruple == (0, 0, 1, 0):
            j -= 1
            """
            ..
            #.
            """
         elif quadruple == (0, 0, 1, 1):
            j -= 1
            """
            ..
            ##
            """
         elif quadruple == (0, 1, 0, 0):
            j += 1
            """
            .#
            ..
            """
         elif quadruple == (0, 1, 0, 1):
            i += 1
            """
            .#
            .#
            """
         elif quadruple == (0, 1, 1, 0):
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
         elif quadruple == (0, 1, 1, 1):
            j -= 1
            """
            .#
            ##
            """
         elif quadruple == (1, 0, 0, 0):
            i -= 1
            """
            #.
            ..
            """
         elif quadruple == (1, 0, 0, 1):
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
         elif quadruple == (1, 0, 1, 0):
            i -= 1
            """
            #.
            #.
            """
         elif quadruple == (1, 0, 1, 1):
            i -= 1
            """
            #.
            ##
            """
         elif quadruple == (1, 1, 0, 0):
            j += 1
            """
            ##
            ..
            """
         elif quadruple == (1, 1, 0, 1):
            i += 1
            """
            ##
            .#
            """
         elif quadruple == (1, 1, 1, 0):
            j += 1
            """
            ##
            #.
            """
         elif quadruple == (1, 1, 1, 1):
            raise RuntimeError("Something really unexpected happened")
            """
            ##
            ##
            """
         else:
            raise RuntimeError("Something REALLY unexpected happened")
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

def contours_to_AS(contours: Contours) -> str:
   with StringIO() as f:
      f.write("new <Vector.<Vertex>>[")
      for contour in contours:
         f.write('new <Vertex>[')
         f.write(', '.join(f'new Vertex{xy}' for xy in contour))
         f.write('],')
      f.write("]\n")
      return f.getvalue()

###################################################################################################
####################################### HERE COMES THE GUI ########################################
###################################################################################################

class FieldNotInitialized(RuntimeError):
   def __init__(self) -> None:
      super().__init__()
      self.message = "For some reason field is still None"

if __name__ == "__main__":
   root = Tk()

   a = 20  # cell size
   w, h = 1000, 400  # canvas width and height
   # Scrollable canvas
   ca = Canvas(root, width=w, height=h)
   ca.bind("<ButtonPress-1>", lambda e: ca.scan_mark(e.x, e.y))
   ca.bind("<B1-Motion>", lambda e: ca.scan_dragto(e.x, e.y, gain=1))

   lazy_results = None
   def gen() -> None:
      global lazy_results
      ca.delete('all')
      ca.xview_moveto(0)
      ca.yview_moveto(0)
      n = tk_n.get()
      if EAGER and n > 8:
         if not messagebox.askyesno("Too big", "Polyominoes with more than 8 cells can take a loooot of time in eager mode. Proceed anyway?"):
            return

      if lazy_results == None:
         lazy_results = polyominoes(n)

      zx, zy = 10, 10

      def draw(result: Field, k: Optional[int] = None) -> None:
         if k == None:
            tag = "p"
         else:
            tag = f"p{k}"

         for i, row in enumerate(result):
            for j, cell in enumerate(row):
               if cell is not Cell.EMPTY:
                  ca.create_rectangle(zx + j * a,
                                      zy + i * a,
                                      zx + j * a + a,
                                      zy + i * a + a,
                                      fill="grey50",
                                      tags=tag)
                  ca.tag_bind(tag, '<ButtonPress-1>', combine(n=n, result=result))
                  ca.tag_bind(tag, '<Enter>', lambda e, tag=tag:
                           [ca.itemconfig(i, fill="red")
                           for i in ca.find_withtag(tag)])
                  ca.tag_bind(tag, '<Leave>', lambda e, tag=tag:
                           [ca.itemconfig(i, fill="grey50")
                           for i in ca.find_withtag(tag)])

      if EAGER:
         if a == 20:
            sx, sy = 100, 100 # step x, step y
         else:
            sx, sy = 60, 60 # step x, step y
         for k, result in enumerate(lazy_results):
            draw(result, k)
            zx += sx
            if zx > w-sx:
               zy += sy
               zx = 10
         gen_b.config(state="disabled")
      else:
         try:
            result = next(lazy_results)
            draw(result)
         except StopIteration:
            gen_b.config(state="disabled")
            messagebox.showinfo("No more pieces", "No more pieces, try another number of cells")

   gen_b = Button(root, text="Generate", command=gen)

   tk_n = IntVar()
   def on_set_n(name1: str, name2: str, op: str) -> None:
      global lazy_results
      lazy_results = polyominoes(tk_n.get())
      gen_b.config(state="active")

   tk_n.trace("w", on_set_n)
   sb = Spinbox(root, from_=1, to=20, textvariable=tk_n) # TODO: 20 is a dumb artificial restriction

   # layout
   ca.grid(row=0, column=0, columnspan=3)
   Label(root, text="Number of cells: ").grid(row=1, column=0, sticky="e")
   sb.grid(row=1, column=1, sticky="w")
   gen_b.grid(row=1, column=2)

   field: Optional[Field] = None
   selected: Optional[str] = None
   figures: Dict[str, List[Hmm]] = {}

   def combine(n: int, result: Field) -> Callback:
      zy = n * a
      def callback(__: Event) -> None:
         cmb = Toplevel(root)
         #cmb.grab_set()
         def on_close() -> None:
            #cmb.grab_release()
            cmb.destroy()
         cmb.protocol('WM_DELETE_WINDOW', on_close)
         cmbca = Canvas(cmb, width=w, height=h)
         cmbca.bind("<ButtonPress-1>", lambda e: cmbca.scan_mark(e.x, e.y))
         cmbca.bind("<B1-Motion>", lambda e: cmbca.scan_dragto(e.x, e.y, gain=1))
         tk_m = IntVar()

         def wrapper(tag: str) -> Callback:
            def toggle_selection(__: Event) -> None:
               global selected
               selected = tag
               for i in cmbca.find_all():
                  cmbca.itemconfig(i, width=1)
               for i in cmbca.find_withtag(tag):
                  cmbca.itemconfig(i, width=2)
            return toggle_selection

         def pl() -> None:
            global field, selected
            selected = None
            cmbca.delete('all')
            cmbca.xview_moveto(0)
            cmbca.yview_moveto(0)
            m = tk_m.get()
            field = [[Cell.EMPTY for __ in range(n * m)] for __ in range(n * m)]
            zx, zn = 0, 0
            while m:
               tag = f"m{m}"
               figures[tag] = []
               zx += n * a
               for i, row in enumerate(result):
                  for j, cell in enumerate(row):
                     if cell is not Cell.EMPTY:
                        cmbca.create_rectangle(zx + j * a,
                                               zy + i * a,
                                               zx + j * a + a,
                                               zy + i * a + a,
                                               fill="grey50",
                                               tags=tag)
                        field[i][zn + j] = Cell.FULL
                        figures[tag].append(Hmm(zn + j, i))
                        cmbca.tag_bind(tag, '<ButtonPress-1>', wrapper(tag=tag))
                        cmbca.tag_bind(tag, '<Enter>', lambda e, tag=tag:
                                   [cmbca.itemconfig(i, fill="red")
                                    for i in cmbca.find_withtag(tag)])
                        cmbca.tag_bind(tag, '<Leave>', lambda e, tag=tag:
                                   [cmbca.itemconfig(i, fill="grey50")
                                    for i in cmbca.find_withtag(tag)])
               m -= 1
               zn += n
            cmbca.create_rectangle(n * a, zy, zx + n * a, zy + zx)

         def export() -> None:
            if field is None:
               raise FieldNotInitialized
            fn = filedialog.asksaveasfilename(defaultextension=".txt",
                                              initialfile="puzzle.txt",
                                              parent=cmb,
                                              title="Append figure to file")
            if fn:
               contours = field_to_contours(field)
               with open(fn, 'a') as f:
                  f.write(contours_to_AS(contours))
               print_field(field)

         exportb = Button(cmb, text="Export figure as <Vector.<Vertex>> (append)", command=export)

         # layout
         Label(cmb,
               text="Select a figure, then press arrows to move it, "\
                    "r to rotate, h or v to reflect across the "\
                    "corresponding axis").grid(row=0, column=0, columnspan=4)
         cmbca.grid(row=1, column=0, columnspan=4)
         Label(cmb, text="Number of figures: ").grid(row=2, column=0, sticky="e")
         Spinbox(cmb, from_=1, to=8, textvariable=tk_m).grid(row=2, column=1, sticky="w")
         Button(cmb, text="Place", command=pl).grid(row=2, column=2)
         exportb.grid(row=2, column=3)

         def transform(kind: Transformation) -> Callback:

            def callback(__: Event) -> None:
               global field, figures
               if field is None:
                  raise FieldNotInitialized
               backup = deepcopy(field), deepcopy(figures)
               if selected is not None:
                  for o in figures[selected]:
                     field[o.y][o.x] = Cell.EMPTY
                  if kind.is_translation:
                     for i in range(n):
                        figures[selected][i].x += kind.dx
                        figures[selected][i].y += kind.dy
                  else:
                     xs = [o.x for o in figures[selected]]
                     ys = [o.y for o in figures[selected]]
                     center_x = min(xs) + (max(xs) - min(xs)) // 2
                     center_y = min(ys) + (max(ys) - min(ys)) // 2
                     for i in range(n):
                        figures[selected][i].x -= center_x
                        figures[selected][i].y -= center_y
                     if kind == Transformation.ROTATE:
                        figures[selected] = [Hmm(-o.y, o.x) for o in figures[selected]]
                     elif kind == Transformation.REFLECT_OVER_VERTICAL_AXIS:
                        figures[selected] = [Hmm(-o.x, o.y) for o in figures[selected]]
                     elif kind == Transformation.REFLECT_OVER_HORIZONTAL_AXIS:
                        figures[selected] = [Hmm(o.x, -o.y) for o in figures[selected]]
                     else: # should never happen
                        warn("Unknown transformation", RuntimeWarning)
                        # raising an exception in the middle of a transaction would be a bad idea
                     for i in range(n):
                        figures[selected][i].x = figures[selected][i].x + center_x
                        figures[selected][i].y = figures[selected][i].y + center_y
                  # validation
                  for o in figures[selected]:
                     try:
                        if o.x < 0 or o.y < 0:  # would violate field boundaries
                           raise IndexError
                        if field[o.y][o.x] is not Cell.EMPTY:
                           # if it raises IndexError:
                           # it means y or x are too large
                           # and violate field boundaries
                           # if field[y][x] is not empty: # TODO: rethink in depth, especially diags
                           # it means collision with another figure
                           raise IndexError
                        field[o.y][o.x] = Cell.FULL # TODO: it needs a detailed comparison to redactor_diag.py
                     except IndexError:  # has violated boundaries in one way or another
                        field, figures = backup  # restoring
                        return
                  if kind.is_translation:
                     cmbca.move(selected, kind.dx * a, kind.dy * a)
                  else:
                     cmbca.delete(selected)
                     for o in figures[selected]:
                        cmbca.create_rectangle((n + o.x) * a,
                                               o.y * a + zy,
                                               (n + o.x + 1) * a,
                                               (o.y + 1) * a + zy,
                                               fill="grey50",
                                               tags=selected)
                        for i in cmbca.find_withtag(selected):
                           cmbca.itemconfig(i, width=2)
            return callback

         cmb.bind('<Up>', transform(Transformation.UP))
         cmb.bind('<Down>', transform(Transformation.DOWN))
         cmb.bind('<Left>', transform(Transformation.LEFT))
         cmb.bind('<Right>', transform(Transformation.RIGHT))
         cmb.bind('r', transform(Transformation.ROTATE))
         cmb.bind('h', transform(Transformation.REFLECT_OVER_HORIZONTAL_AXIS))
         cmb.bind('v', transform(Transformation.REFLECT_OVER_VERTICAL_AXIS))
      return callback

   root.mainloop()
