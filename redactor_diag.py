from redactor import no_empty_rows_cols, get_dims, fill

def connected(t, n, H, W):
   """
   '  '	0
   '|/'	1
   '/|'	2
   '\|'	3
   '|\'	4
   '|_|'	5
   """
   t_mutable = list(t)
   def fill4(x, y):
      xy = x+W*y
      if t_mutable[xy] > 0:
         me = t_mutable[xy]
         t_mutable[xy] = -t_mutable[xy]
         if y+1 < H:
            nb = t_mutable[x+W*(y+1)] #test neighbor
            if me in(2,4,5) and nb in (1,3,5):
               fill4(x, y+1)
         if 0 < y:
            nb = t_mutable[x+W*(y-1)]
            if me in (1,3,5) and nb in (2,4,5):
               fill4(x, y-1)
         if 0 < x:
            nb = t_mutable[(x-1)+W*y]
            if me in (1,4,5) and nb in (2,3,5):
               fill4(x-1, y)
         if x+1 < W:
            nb = t_mutable[(x+1)+W*y]
            if me in (2,3,5) and nb in (1,4,5):
               fill4(x+1, y)
   for i,c in enumerate(t):
      if c:
         break
   fill4(i%W, i//W)
   result = len([c for c in t_mutable if c < 0]) == n
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
   from itertools import product
   from math import sqrt, floor, ceil
   result = set()
   for H in range(ceil(sqrt(n)), n + 1):
      for W in range(ceil(n/H), min([n + 1 - H, H]) + 1):  # W <= H and W*H >= n and W-1+H-1 <= n-1
         for t in product(range(6), repeat=H * W):
            if sum(1 for i in t if i) == n and no_empty_rows_cols(t, H, W) and connected(t, n, H, W):
               polyomino = tuple(tuple(t[x + W * y] for x in range(W)) for y in range(H))
               # TODO: maybe profile how much time is actually spent here with checking the symmetries
               # ESPECIALLY for longer lists towards their end
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
               result.add(polyomino)
               yield polyomino

def rotate(matrix):
   "rotates by 90 degrees clockwise"
   d = {0:0, 1:3, 2:4, 3:2, 4:1, 5:5}
   return tuple(tuple(d[elem] for elem in row[::-1]) for row in zip(*matrix))

def v_reflect(matrix):
   "reflects across the vertical axis"
   d = {0:0, 1:3, 2:4, 3:1, 4:2, 5:5}
   return tuple(tuple(d[elem] for elem in row[::-1]) for row in matrix)

def h_reflect(matrix):
   "reflects across the horizontal axis"
   d = {0:0, 1:4, 2:3, 3:2, 4:1, 5:5}
   return tuple(tuple(d[elem] for elem in row) for row in matrix[::-1])

######################################################
##### Neither generation-related nor GUI-related #####
######################################################

def find_zeroth_vertex(field):
   # currently: find the leftmost of the uppermost filled cells
   for i, row in enumerate(field):
      for j, cell in enumerate(row):
         if cell:
            quadruple = get_quadruple(field, i, j)
            normalize_quadruple(quadruple)
            if quadruple != [0,0,0,0]: # TODO: add other illegal starting points
               print("START AT", quadruple)
               return j, i
   
def normalize_quadruple(quadruple):
   # THIS FUNCTION MUTATES ITS ARGUMENT (and returns None)
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

def get_quadruple(field, i, j):
   nrows, ncols = get_dims(field)
   return [field[i - 1][j - 1] if i > 0 and j > 0 else 0,
           field[i - 1][j] if i > 0 and j < ncols else 0,
           field[i][j - 1] if i < nrows and j > 0 else 0,
           field[i][j] if i < nrows and j < ncols else 0]

def field_to_contours(field):
   field = [[5 if i>5 else i for i in row] for row in field] # coercing 5,6,7 to 5
   # TODO: check if connected
   
   # adding an empty top row, an empty bottom row, an empty right column and an empty left column
   # this is done to make sure the outer empty part (without the holes) is contiguous
   nrows, ncols = get_dims(field)
   field = [[0] * (ncols+2)] + [[0] + row + [0] for row in field] + [[0] * (ncols+2)]

   # inner function to get one of the contours
   def field_to_one_contour(field):
      j, i = find_zeroth_vertex(field)
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
      contours.append(reversed(contour))            
   
   centered = [[(x - meanX, y - meanY) for x, y in contour] for contour in contours]
   return centered

###################################################################################################
####################################### HERE COMES THE GUI ########################################
###################################################################################################

from tkinter import Tk, Toplevel, Canvas, Label, Spinbox, Button, IntVar, messagebox

compatibles = [(0,i) for i in range(1,6)]
compatibles.extend([(1,2), (3,4)])
compatibles.extend([(j,i) for (i,j) in compatibles])

if __name__ == "__main__":
   root = Tk()

   a = 20  # cell size
   w, h = 1000, 400  # canvas width and height
   # Scrollable canvas
   ca = Canvas(root, width=w, height=h)
   ca.bind("<ButtonPress-1>", lambda e: ca.scan_mark(e.x, e.y))
   ca.bind("<B1-Motion>", lambda e: ca.scan_dragto(e.x, e.y, gain=1))
   
   def paint_cell(cell, canvas, x0, y0, i, j, tag):
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

   results = None # will turn into a polyominoes generator later
   def next_piece():
      global result
      ca.delete('all')
      ca.xview_moveto(0)
      ca.yview_moveto(0)
      try:
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
   def on_set_n(*args):
      global results
      next_b.config(state="active")
      results = polyominoes(tk_n.get())
   tk_n.trace("w", on_set_n)
   sb = Spinbox(root, from_=1, to = 20, textvariable=tk_n)
   tk_n.set(5)
   
   # layout
   ca.grid(row=0, column=0, columnspan=2)
   Label(root, text="Number of cells: ").grid(row=1, column=0, sticky="e")
   sb.grid(row=1, column=1, sticky="w")
   next_b.grid(row=1, column=2)

   field = None
   selected = None
   figures = {}
   def combine(n):
      zy = n * a
      def callback(e):
         cmb = Toplevel(root)
         #cmb.grab_set()
         def on_close():
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
         
         def wrapper(tag):
            def toggle_selection(e):
               global selected
               selected = tag
               for i in cmbca.find_all():
                  cmbca.itemconfig(i, width=1)
               for i in cmbca.find_withtag(tag):
                  cmbca.itemconfig(i, width=2)
               cmbca.tag_raise(selected)
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
         
         def export():
            from tkinter import filedialog
            fn = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="puzzle.txt", parent=cmb, title="Append figure to file")
            if fn:
               contours = field_to_contours(field)
               with open(fn, 'a') as f:
                  f.write('new <Vector.<Vertex>>[')
                  for contour in contours:
                     f.write('new <Vertex>[')
                     f.write(', '.join('new Vertex{}'.format(xy) for xy in contour))
                     f.write('],')
                  f.write("]\n")
         
         def preview():
            from random import randint
            prvw.delete("all")
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
         
         def transform(kind):
            from copy import deepcopy
            from warnings import warn
            def callback(e):
               global field, figures
               backup = [deepcopy(field), deepcopy(figures)]
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
                     center_x, center_y = min(xs) + (max(xs) - min(xs)) / 2, min(ys) + (max(ys) - min(ys)) / 2
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