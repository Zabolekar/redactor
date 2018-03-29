# for python2: from __future__ import division, int(ceil(...)) instead of ceil(...) and tkinter => Tkinter

def no_empty_rows_cols(t, H, W):
   for row in range(H):
      if not 1 in (t[(row * W):((row + 1) * W)]):
         return False
   for col in range(W):
      if not 1 in (t[col::W]):
         return False
   return True

def connected(t, n, H, W):
   t_mutable = list(t)
   def fill4(x, y):
      xy = x+W*y
      if t_mutable[xy] == 1:
         t_mutable[xy] = 2
         if y+1 < H and t_mutable[x+W*(y+1)]:
            fill4(x, y+1)
         if 0 < y and t_mutable[x+W*(y-1)]:
            fill4(x, y-1)
         if 0 < x and t_mutable[(x-1)+W*y]:
            fill4(x-1, y)
         if x+1 < W and t_mutable[(x+1)+W*y]:
            fill4(x+1, y)
   for i,c in enumerate(t):
      if c:
         break
   fill4(i%W, i//W)
   result = len([c for c in t_mutable if c == 2]) == n
   return result
   
def polyominoes(n):
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
   # TODO: ISSUE SOME WARNING FOR polyominoes(9) and above
   from itertools import product
   from math import sqrt, floor, ceil
   result = []
   for H in range(ceil(sqrt(n)), n + 1):
      for W in range(ceil(n/H), min([n + 1 - H, H]) + 1):  # W <= H and W*H >= n and W-1+H-1 <= n-1
         for t in product([0, 1], repeat=H * W):
            if sum(t) == n and no_empty_rows_cols(t, H, W) and connected(t, n, H, W):
               polyomino = [[t[x + W * y] for x in range(W)] for y in range(H)]
               # check symmetries
               v_reflected = v_reflect(polyomino)
               if v_reflected in result:
                  continue
               h_reflected = h_reflect(polyomino)
               if h_reflected in result:
                  continue
               vh_reflected = h_reflect(v_reflected)
               if vh_reflected in result:
                  continue
               # if it is square, then additionally check rotations of every one of the four by 90
               if len(polyomino) == len(polyomino[0]):
                  if rotate(polyomino) in result:
                     continue
                  if rotate(v_reflected) in result:
                     continue
                  if rotate(h_reflected) in result:
                     continue
                  if rotate(vh_reflected) in result:
                     continue
               # finally, if we didn't find any transformation of it in our list
               result.append(polyomino)
               yield polyomino

def rotate(matrix):
   "rotates by 90 degrees"
   return [list(row[::-1]) for row in zip(*matrix)]

def v_reflect(matrix):
   "reflects across the vertical axis"
   return [row[::-1] for row in matrix]

def h_reflect(matrix):
   "reflects across the horizontal axis"
   return matrix[::-1]

######################################################
##### Neither generation-related nor GUI-related #####
######################################################

def print_field(field):
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

def fill(field, y, x, new_value):
   nrows, ncols = len(field), len(field[0])
   old_value = field[y][x]
   auxiliary_field = [['unchecked' for __ in row] for row in field]
   # auxiliary_field cell can has three distinct values: unchecked 0, about to be checked 1, being checked now 2, checked 3
   auxiliary_field[y][x] = 'being checked'
   while sum('being checked' in row for row in auxiliary_field):
      for y in range(nrows):
         for x in range(ncols):
            if auxiliary_field[y][x] == 'being checked':
               neighbours = []
               # regular neighbours
               if y > 0: neighbours.append((y - 1, x))
               if y + 1 < nrows: neighbours.append((y + 1, x))
               if x > 0: neighbours.append((y, x - 1))
               if x + 1 < ncols: neighbours.append((y, x + 1))
               # diagonal neighbours
               if y > 0 and x > 0: neighbours.append((y - 1, x - 1))
               if y + 1 < nrows and x > 0: neighbours.append((y + 1, x - 1))
               if y > 0 and x + 1 < ncols: neighbours.append((y - 1, x + 1))
               if y + 1 < nrows and x + 1 < ncols: neighbours.append((y + 1, x + 1))
               for ny, nx in neighbours:
                  if auxiliary_field[ny][nx] == 'unchecked' and field[ny][nx] == old_value:
                     auxiliary_field[ny][nx] = 'to be checked'
               auxiliary_field[y][x] = 'checked'
      for y in range(nrows):
         for x in range(ncols):
            if auxiliary_field[y][x] == 'to be checked':
               auxiliary_field[y][x] = 'being checked'
   result = [[i for i in row] for row in field]  # copying
   # actually filling:
   for y in range(nrows):
      for x in range(ncols):
         if auxiliary_field[y][x] == 'checked':
            result[y][x] = new_value
   return result

def field_to_contours(field):
   # TODO: check if connected
   
   # adding an empty top row, an empty bottom row, an empty right column and an empty left column
   # this is done to make sure the outer empty part (without the holes) is contiguous
   nrows, ncols = len(field) + 2, len(field[0]) + 2
   field = [[0] * ncols] + [[0] + row + [0] for row in field] + [[0] * ncols]

   # inner function to get one of the contours
   def field_to_one_contour(field):
      # find the leftmost of the uppermost filled cells
      break_flag = False
      for i, row in enumerate(field):
         if sum(row):
            for j, cell in enumerate(row):
               if cell:
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
   holes_inverted = [[{1:0, 0:1}[i] for i in row] for row in fill(field, 0, 0, 1)]

   # actually find the holes and add them (reversed) to contours
   while sum(map(sum, holes_inverted)):
      contour = field_to_one_contour(holes_inverted)
      j, i = contour[0]
      holes_inverted = fill(holes_inverted, i, j, 0)
      contours.append(reversed(contour))            
   
   centered = [[(x - meanX, y - meanY) for x, y in contour] for contour in contours]
   return centered

def contours_to_AS(contours):
   outer_prefix = 'new <Vector.<Vertex>>['      
   outer_postfix = '],\n'
   inner_prefix = 'new <Vertex>['
   inner_postfix = '],'
   return (outer_prefix
           + ''.join(inner_prefix
                     + ', '.join('new Vertex{}'.format(xy) for xy in contour)
                     + inner_postfix
                     for contour in contours)
           + outer_postfix)

###################################################################################################
####################################### HERE COMES THE GUI ########################################
###################################################################################################

from tkinter import Tk, Toplevel, Canvas, Label, Spinbox, Button, IntVar

if __name__ == "__main__":
   root = Tk()

   a = 20  # cell size
   w, h = 1000, 400  # canvas width and height
   # Scrollable canvas
   ca = Canvas(root, width=w, height=h)
   ca.bind("<ButtonPress-1>", lambda e: ca.scan_mark(e.x, e.y))
   ca.bind("<B1-Motion>", lambda e: ca.scan_dragto(e.x, e.y, gain=1))

   results = None
   def gen():
      global results
      ca.delete('all')
      ca.xview_moveto(0)
      ca.yview_moveto(0)
      n = tk_n.get()
      results = list(polyominoes(n))
      zx, zy = 10, 10
      if a == 20:
         sx, sy = 100, 100 # step x, step y
      else:
         sx, sy = 60, 60 # step x, step y
      for k, result in enumerate(results):
         tag = "p{}".format(k)
         for i, row in enumerate(result):
            for j, cell in enumerate(row):
               if cell:
                  ca.create_rectangle(zx + j * a, zy + i * a, zx + j * a + a, zy + i * a + a, fill="grey50", tags=tag)
                  ca.tag_bind(tag, '<ButtonPress-1>', combine(k=k, n=n))
                  ca.tag_bind(tag, '<Enter>', lambda e, tag=tag:
                           [ca.itemconfig(i, fill="red")
                           for i in ca.find_withtag(tag)])
                  ca.tag_bind(tag, '<Leave>', lambda e, tag=tag:
                           [ca.itemconfig(i, fill="grey50")
                           for i in ca.find_withtag(tag)])
         zx += sx
         if zx > w-sx:
            zy += sy
            zx = 10
      gen_b.config(state="disabled")

   gen_b = Button(root, text="Generate", command=gen)

   tk_n = IntVar()
   tk_n.trace("w", lambda *args: gen_b.config(state="active"))
   sb = Spinbox(root, from_=1, to=8, textvariable=tk_n)

   # layout
   ca.grid(row=0, column=0, columnspan=3)
   Label(root, text="Number of cells: ").grid(row=1, column=0, sticky="e")
   sb.grid(row=1, column=1, sticky="w")
   gen_b.grid(row=1, column=2)

   field = None
   selected = None
   figures = {}
   def combine(k, n):
      zy = n * a
      def callback(e):
         result = results[k]
         cmb = Toplevel(root)
         cmb.grab_set()
         def on_close():
            cmb.grab_release()
            cmb.destroy()
         cmb.protocol('WM_DELETE_WINDOW', on_close)
         cmbca = Canvas(cmb, width=w, height=h)
         cmbca.bind("<ButtonPress-1>", lambda e: cmbca.scan_mark(e.x, e.y))
         cmbca.bind("<B1-Motion>", lambda e: cmbca.scan_dragto(e.x, e.y, gain=1))
         tk_m = IntVar()
         
         def wrapper(tag):
            def toggle_selection(e):
               global selected
               selected = tag
               for i in cmbca.find_all():
                  cmbca.itemconfig(i, width=1)
               for i in cmbca.find_withtag(tag):
                  cmbca.itemconfig(i, width=2)
            return toggle_selection
         
         def pl():
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
                        cmbca.create_rectangle(zx + j * a, zy + i * a, zx + j * a + a, zy + i * a + a, fill="grey50", tags=tag)
                        field[i][zn + j] = 1
                        figures[tag].append([zn + j, i])
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
         
         def export():
            from tkinter import filedialog
            fn = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="puzzle.txt", parent=cmb, title="Append figure to file")
            if fn:
               contours = field_to_contours(field)
               with open(fn, 'a') as f:
                  f.write(contours_to_AS(contours))
               print_field(field)
               
         exportb = Button(cmb, text="Export figure as <Vector.<Vertex>> (append)", command=export)
         
         # layout
         Label(cmb, text="Select a figure, then press arrows to move it, r to rotate, h or v to reflect across the corresponding axis").grid(row=0, column=0, columnspan=4)
         cmbca.grid(row=1, column=0, columnspan=4)
         Label(cmb, text="Number of figures: ").grid(row=2, column=0, sticky="e")
         Spinbox(cmb, from_=1, to=8, textvariable=tk_m).grid(row=2, column=1, sticky="w")
         Button(cmb, text="Place", command=pl).grid(row=2, column=2)
         exportb.grid(row=2, column=3)
         
         def transform(kind):
            from copy import deepcopy
            from warnings import warn
            def callback(e):
               global field, figures
               backup = [deepcopy(field), deepcopy(figures)]
               if selected:
                  for x, y in figures[selected]:
                        field[y][x] = 0
                  is_translation = kind in ["up", "down", "left", "right"]
                  if is_translation:
                     dx = {"up": 0, "down": 0, "left":-1, "right": 1}[kind]
                     dy = {"up":-1, "down": 1, "left": 0, "right": 0}[kind]               
                     for i in range(n):
                        figures[selected][i][0] += dx
                        figures[selected][i][1] += dy
                  else:
                     xs, ys = [x for x, y in figures[selected]], [y for x, y in figures[selected]]
                     center_x, center_y = min(xs) + (max(xs) - min(xs)) / 2, min(ys) + (max(ys) - min(ys)) / 2
                     for i in range(n):
                        figures[selected][i][0] -= center_x
                        figures[selected][i][1] -= center_y
                     if kind == "rotate":
                        figures[selected] = [[-y, x] for x, y in figures[selected]]
                     elif kind == "reflect|":
                        figures[selected] = [[-x, y] for x, y in figures[selected]]
                     elif kind == "reflect-":
                        figures[selected] = [[x, -y] for x, y in figures[selected]]
                     else:
                        warn("Unknown transformation", RuntimeWarning)  # raising an exception in the middle of a transaction would be a bad idea
                     for i in range(n):
                        figures[selected][i][0] = int(figures[selected][i][0] + center_x)
                        figures[selected][i][1] = int(figures[selected][i][1] + center_y)
                  # validation
                  for x, y in figures[selected]:
                     try:
                        if x < 0 or y < 0:  # would disrespect field boundaries
                           raise IndexError
                        if field[y][x]:
                           # raises IndexError if y or x too large (so they disrespect field boundaries)
                           # if True than it means collision with another figure
                           raise IndexError
                        field[y][x] += 1
                     except IndexError:  # has disrespected boundaries in one way or another
                        field, figures = backup  # restoring
                        return
                  if is_translation:
                     cmbca.move(selected, dx * a, dy * a)
                  else:
                     cmbca.delete(selected)
                     for x, y in figures[selected]:
                        cmbca.create_rectangle((n + x) * a, y * a + zy, (n + x + 1) * a, (y + 1) * a + zy, fill="grey50", tags=selected)
                        for i in cmbca.find_withtag(selected):
                           cmbca.itemconfig(i, width=2)
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