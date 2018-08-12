from tkinter import Tk, Toplevel, Canvas, Label, Spinbox, Button, IntVar, Event, filedialog, messagebox
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple
from itertools import product
from math import sqrt, floor, ceil
from copy import deepcopy
from warnings import warn
from random import randint
from redactor import (no_empty_rows_cols, get_dims, fill, polyominoes,
                      Vertex, Contour, Contours, Row, Field, Callback)

import redactor
redactor.DIAG = True
redactor.EAGER = False

######################################################
##### Neither generation-related nor GUI-related #####
######################################################

def find_zeroth_vertex(field: Field) -> Optional[Tuple[int, int]]:
   # currently: find the leftmost of the uppermost filled cells
   for i, row in enumerate(field):
      for j, cell in enumerate(row):
         if cell:
            quadruple = get_quadruple(field, i, j)
            normalize_quadruple(quadruple)
            if quadruple != [0,0,0,0]: # TODO: add other illegal starting points
               print("START AT", quadruple)
               return j, i
   return None
   
def normalize_quadruple(quadruple: List[int]) -> None:
   """THIS FUNCTION MUTATES ITS ARGUMENT"""
   # Validate quadruple, just in case:
   if len(quadruple) != 4:
      raise ValueError(f"Invalid quadruple {quadruple}")
   # There are 6^4 = 1296 possible quadruples to consider (although some of them, like 0000 or 5555, should never happen)
   # it would not be wise to list all of them as we did in older redactor versions, without diagonals
   # So we do it a bit differently:
   if quadruple[0] == 1:
      quadruple[0] = 0
   elif quadruple[0] == 2:
      quadruple[0] = 5
   if quadruple[1] == 3:
      quadruple[1] = 0
   elif quadruple[1] == 4:
      quadruple[1] = 5
   if quadruple[2] == 3:
      quadruple[2] = 5
   elif quadruple[2] == 4:
      quadruple[2] = 0
   if quadruple[3] == 1:
      quadruple[3] = 5
   elif quadruple[3] == 2:
      quadruple[3] = 0
   # now only 256 possible quadruples remain (and some of them should never happen)

def get_quadruple(field: Field, i: int, j: int) -> List[int]:
   nrows, ncols = get_dims(field)
   return [field[i - 1][j - 1] if i > 0 and j > 0 else 0,
           field[i - 1][j] if i > 0 and j < ncols else 0,
           field[i][j - 1] if i < nrows and j > 0 else 0,
           field[i][j] if i < nrows and j < ncols else 0]

def field_to_contours(field: Field) -> Contours:
   field = [[5 if i>5 else i for i in row] for row in field] # coercing 5,6,7 to 5
   # TODO: check if connected
   
   # adding an empty top row, an empty bottom row, an empty right column and an empty left column
   # this is done to make sure the outer empty part (without the holes) is contiguous
   nrows, ncols = get_dims(field)
   field = [[0] * (ncols+2)] + [[0] + row + [0] for row in field] + [[0] * (ncols+2)]

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
            raise RuntimeError("Something unexpected happened, quadruple is {}".format(quadruple))
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
   holes_inverted = [[{0:5, 1:2, 2:1, 3:4, 4:3, 5:0}[i] for i in row] for row in fill(field, 0, 0, 5)]

   # actually find the holes and add them (reversed) to contours
   while sum(map(sum, holes_inverted)):
      contour = field_to_one_contour(holes_inverted)
      j, i = contour[0]
      holes_inverted = fill(holes_inverted, i, j, 0)
      contours.append(list(reversed(contour)))
   
   centered = [[(x - meanX, y - meanY) for x, y in contour] for contour in contours]
   return centered

###################################################################################################
####################################### HERE COMES THE GUI ########################################
###################################################################################################

compatibles = [(0,i) for i in range(1,6)]
compatibles.extend([(1,2), (3,4)])
compatibles.extend([(j,i) for (i,j) in compatibles])

result: Field

if __name__ == "__main__":
   root = Tk()

   a = 20  # cell size
   w, h = 1000, 400  # canvas width and height
   # Scrollable canvas
   ca = Canvas(root, width=w, height=h)
   ca.bind("<ButtonPress-1>", lambda e: ca.scan_mark(e.x, e.y))
   ca.bind("<B1-Motion>", lambda e: ca.scan_dragto(e.x, e.y, gain=1))
   
   def paint_cell(cell: int, canvas: Canvas, x0: int, y0: int, i: int, j: int, tag: str) -> None:
      if cell == 5:
         canvas.create_rectangle(x0+j*a, y0+i*a, x0+j*a+a, y0+i*a+a, fill="grey50", tags=tag)
      elif cell == 4:
         canvas.create_polygon(x0+j*a, y0+i*a, x0+j*a, y0+i*a+a, x0+j*a+a, y0+i*a+a, fill="grey50", tags=tag, outline = "black")
      elif cell == 3:
         canvas.create_polygon(x0+j*a+a, y0+i*a, x0+j*a, y0+i*a, x0+j*a+a, y0+i*a+a, fill="grey50", tags=tag, outline = "black")
      elif cell == 2:
         canvas.create_polygon(x0+j*a+a, y0+i*a, x0+j*a, y0+i*a+a, x0+j*a+a, y0+i*a+a, fill="grey50", tags=tag, outline = "black")
      elif cell == 1:
         canvas.create_polygon(x0+j*a, y0+i*a, x0+j*a+a, y0+i*a, x0+j*a, y0+i*a+a, fill="grey50", tags=tag, outline = "black")

   results: Optional[Iterator[Field]] = None # will turn into a polyominoes generator later
   def next_piece() -> None:
      global result
      ca.delete('all')
      ca.xview_moveto(0)
      ca.yview_moveto(0)
      try:
         if results is None:
            raise ValueError("This is a bug, we forgot to initialize results")
         result = next(results)
      except StopIteration:
         next_b.config(state="disabled")
         messagebox.showinfo("No more pieces", "No more pieces, try another number of cells")
         return
      for i, row in enumerate(result):
         for j, cell in enumerate(row):
            paint_cell(cell, ca, a, h//2, i, j, "p")
      ca.tag_bind("p", '<ButtonPress-1>', combine(tk_n.get()))
      ca.tag_bind("p", '<Enter>', lambda __:
               [ca.itemconfig(i, fill="red") 
               for i in ca.find_withtag("p")])
      ca.tag_bind("p", '<Leave>', lambda __:
               [ca.itemconfig(i, fill="grey50")
               for i in ca.find_withtag("p")])

   next_b = Button(root, text="Next", command=next_piece)

   tk_n = IntVar()
   def on_set_n(name1: str, name2: str, op: str) -> None:
      global results
      results = polyominoes(tk_n.get())
      next_b.config(state="active")

   tk_n.trace("w", on_set_n)
   sb = Spinbox(root, from_=1, to = 20, textvariable=tk_n)
   tk_n.set(4)
   
   # layout
   ca.grid(row=0, column=0, columnspan=2)
   Label(root, text="Number of cells: ").grid(row=1, column=0, sticky="e")
   sb.grid(row=1, column=1, sticky="w")
   next_b.grid(row=1, column=2)

   field = None
   selected = None
   figures: Dict[str, Field] = {}
   def combine(n: int) -> Callback:
      zy = n * a
      def callback(e: Event) -> None:
         cmb = Toplevel(root)
         #cmb.grab_set()
         def on_close() -> None:
            #cmb.grab_release()
            cmb.destroy()
         cmb.protocol('WM_DELETE_WINDOW', on_close)
         cmbca = Canvas(cmb, width=w, height=h)
         prvw = Canvas(cmb, width=400, height=h)
         cmbca.bind("<ButtonPress-1>", lambda e: cmbca.scan_mark(e.x, e.y))
         cmbca.bind("<B1-Motion>", lambda e: cmbca.scan_dragto(e.x, e.y, gain=1))
         prvw.bind("<ButtonPress-1>", lambda e: prvw.scan_mark(e.x, e.y))
         prvw.bind("<B1-Motion>", lambda e: prvw.scan_dragto(e.x, e.y, gain=1))
         tk_m = IntVar()
         
         def wrapper(tag: str) -> Callback:
            def toggle_selection(e: Event) -> None:
               global selected
               selected = tag
               for i in cmbca.find_all():
                  cmbca.itemconfig(i, width=1)
               for i in cmbca.find_withtag(tag):
                  cmbca.itemconfig(i, width=2)
               cmbca.tag_raise(selected)
            return toggle_selection
         
         def pl() -> None:
            global field, selected
            selected = None
            cmbca.delete('all')
            cmbca.xview_moveto(0)
            cmbca.yview_moveto(0)
            m = tk_m.get()
            field = [[0 for __ in range(n * m)] for __ in range(n * m)]
            zx, zn = 0, 0
            while m:
               tag = "m{}".format(m)
               figures[tag] = []
               zx += n * a
               for i, row in enumerate(result):
                  for j, cell in enumerate(row):
                     if cell:
                        field[i][zn + j] = cell
                        paint_cell(cell, cmbca, zx, zy, i, j, tag)
                        figures[tag].append([zn + j, i, cell])
               cmbca.tag_bind(tag, '<ButtonPress-1>', wrapper(tag=tag))
               cmbca.tag_bind(tag, '<Enter>', lambda __, tag=tag:
                          [cmbca.itemconfig(i, fill="red")
                           for i in cmbca.find_withtag(tag)])
               cmbca.tag_bind(tag, '<Leave>', lambda __, tag=tag:
                          [cmbca.itemconfig(i, fill="grey50")
                           for i in cmbca.find_withtag(tag)])
               m -= 1
               zn += n
            cmbca.create_rectangle(n * a, zy, zx + n * a, zy + zx)
            previewb['state'] = 'normal'
            exportb['state'] = 'normal'
         
         def export() -> None:
            fn = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="puzzle.txt", parent=cmb, title="Append figure to file")
            if fn:
               if field is None:
                  raise ValueError("Forgot to initialize 'field', this is a bug")
               contours = field_to_contours(field)
               with open(fn, 'a') as f:
                  f.write('new <Vector.<Vertex>>[')
                  for contour in contours:
                     f.write('new <Vertex>[')
                     f.write(', '.join('new Vertex{}'.format(xy) for xy in contour))
                     f.write('],')
                  f.write("]\n")
         
         def preview() -> None:
            prvw.delete("all")
            if field is None:
               raise ValueError("Forgot to initialize 'field', this is a bug")
            contours = field_to_contours(field)
            for contour in contours:
               color = "#{:03x}".format(randint(0,4095))
               x, y = zip(*((i*40+200, j*40+200) for i,j in contour))
               i, N = 0, len(contour)-1
               while i < N:
                  prvw.create_line(x[i], y[i], x[i+1], y[i+1], arrow="last", width=2, fill=color)
                  i += 1
         
         previewb = Button(cmb, text="Preview: what will be exported?", command=preview)
         previewb['state'] = 'disabled'
         exportb = Button(cmb, text="Export figure as <Vector.<Vertex>> (append)", command=export)
         exportb['state'] = 'disabled'
         
         # layout
         Label(cmb, text="Select a figure, then press arrows to move it, r to rotate, h or v to reflect across the corresponding axis").grid(row=0, column=0, columnspan=4)
         cmbca.grid(row=1, column=0, columnspan=4)
         prvw.grid(row=1, column=4)
         Label(cmb, text="Number of figures: ").grid(row=2, column=0, sticky="e")
         Spinbox(cmb, from_=1, to=20, textvariable=tk_m).grid(row=2, column=1, sticky="w")
         Button(cmb, text="Place", command=pl).grid(row=2, column=2)
         previewb.grid(row=2, column=3)
         exportb.grid(row=2, column=4)
         
         def transform(kind: str) -> Callback:
            def callback(e: Event) -> None:
               global field, figures
               if field is None:
                  raise ValueError("Forgot to initialize 'field', this is a bug")
               backup = deepcopy(field), deepcopy(figures)
               if selected:
                  for x, y, cell in figures[selected]:
                     if field[y][x] == 6:
                        field[y][x] = 3-cell # because 6 can only appear if we superimpose 1 and 2, see below
                     else:
                        field[y][x] -= cell
                  is_translation = kind in ["up", "down", "left", "right"]
                  if is_translation:
                     dx = {"up": 0, "down": 0, "left":-1, "right": 1}[kind]
                     dy = {"up":-1, "down": 1, "left": 0, "right": 0}[kind]               
                     for i in range(n):
                        figures[selected][i][0] += dx
                        figures[selected][i][1] += dy
                  else:
                     xs, ys = [x for x, y, __ in figures[selected]], [y for x, y, __ in figures[selected]]
                     center_x, center_y = min(xs) + (max(xs) - min(xs)) // 2, min(ys) + (max(ys) - min(ys)) // 2
                     for i in range(n):
                        figures[selected][i][0] -= center_x
                        figures[selected][i][1] -= center_y
                     if kind == "rotate":
                        d = {0:0, 1:3, 2:4, 3:2, 4:1, 5:5}
                        figures[selected] = [[-y, x, d[cell]] for x, y, cell in figures[selected]]
                     elif kind == "reflect|":
                        d = {0:0, 1:3, 2:4, 3:1, 4:2, 5:5}
                        figures[selected] = [[-x, y, d[cell]] for x, y, cell in figures[selected]]
                     elif kind == "reflect-":
                        d = {0:0, 1:4, 2:3, 3:2, 4:1, 5:5}
                        figures[selected] = [[x, -y, d[cell]] for x, y, cell in figures[selected]]
                     else:
                        warn("Unknown transformation", RuntimeWarning)  # raising an exception in the middle of a transaction would be a bad idea
                     for i in range(n):
                        figures[selected][i][0] = int(figures[selected][i][0] + center_x)
                        figures[selected][i][1] = int(figures[selected][i][1] + center_y)
                  # validation
                  for x, y, cell in figures[selected]:
                     try:
                        if x < 0 or y < 0:  # would disrespect field boundaries
                           raise IndexError
                        other = field[y][x]
                        # raises IndexError if y or x too large (so they disrespect field boundaries)
                        # and now we actually compare the two cells
                        # to find out if there is a collision with another figure
                        if (cell, other) not in compatibles:
                           raise IndexError
                        if (cell, other) in [(1,2), (2,1)]:
                           field[y][x] = 6 # because 3 would be confused with another state
                        else: #(0,n) (n,0) (3,4) (4,3)
                           field[y][x] += cell
                     except IndexError:  # has disrespected boundaries in one way or another
                        field, figures = backup  # restoring
                        return
                  if is_translation:
                     cmbca.move(selected, dx * a, dy * a)
                  else:
                     cmbca.delete(selected)
                     for x, y, cell_type in figures[selected]:
                        paint_cell(cell_type, cmbca, n*a, zy, y, x, selected)
                        cmbca.tag_raise(selected)
                        for item in cmbca.find_withtag(selected):
                           cmbca.itemconfig(item, width=2)
            return callback
         cmb.bind('<Up>', transform("up"))
         cmb.bind('<Down>', transform("down"))
         cmb.bind('<Left>', transform("left"))
         cmb.bind('<Right>', transform("right"))
         cmb.bind('r', transform("rotate"))
         cmb.bind('h', transform("reflect-"))
         cmb.bind('v', transform("reflect|"))
      return callback

   root.mainloop()