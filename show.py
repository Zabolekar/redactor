# this file is only here to help me visualize the quadruples

import tkinter

quadruples = iter([
 (0, 0, 1, 3),
 (0, 0, 1, 4),
 (0, 0, 1, 5),
 (0, 0, 2, 3),
 (0, 0, 5, 3),
 (0, 1, 0, 3),
 (0, 1, 0, 4),
 (0, 1, 0, 5),
 (0, 1, 1, 0),
 (0, 1, 1, 3),
 (0, 1, 1, 4),
 (0, 1, 1, 5),
 (0, 1, 2, 0),
 (0, 1, 2, 3),
 (0, 1, 2, 4),
 (0, 1, 2, 5),
 (0, 1, 5, 0),
 (0, 1, 5, 3),
 (0, 1, 5, 4),
 (0, 1, 5, 5),
 (0, 2, 0, 4),
 (0, 2, 1, 0),
 (0, 2, 1, 3),
 (0, 2, 1, 4),
 (0, 2, 1, 5),
 (0, 2, 2, 0),
 (0, 2, 2, 3),
 (0, 2, 2, 4),
 (0, 2, 5, 0),
 (0, 2, 5, 3),
 (0, 2, 5, 4),
 (0, 5, 0, 4),
 (0, 5, 1, 0),
 (0, 5, 1, 3),
 (0, 5, 1, 4),
 (0, 5, 1, 5),
 (0, 5, 2, 0),
 (0, 5, 2, 3),
 (0, 5, 2, 4),
 (0, 5, 5, 0),
 (0, 5, 5, 3),
 (0, 5, 5, 4),
 (3, 0, 0, 3),
 (3, 0, 0, 4),
 (3, 0, 0, 5),
 (3, 0, 1, 0),
 (3, 0, 1, 3),
 (3, 0, 1, 4),
 (3, 0, 1, 5),
 (3, 0, 2, 0),
 (3, 0, 2, 3),
 (3, 0, 2, 4),
 (3, 0, 2, 5),
 (3, 0, 5, 0),
 (3, 0, 5, 3),
 (3, 0, 5, 4),
 (3, 0, 5, 5),
 (3, 1, 0, 3),
 (3, 1, 0, 4),
 (3, 1, 0, 5),
 (3, 1, 1, 0),
 (3, 1, 1, 3),
 (3, 1, 1, 4),
 (3, 1, 1, 5),
 (3, 1, 2, 0),
 (3, 1, 2, 3),
 (3, 1, 2, 4),
 (3, 1, 2, 5),
 (3, 1, 5, 0),
 (3, 1, 5, 3),
 (3, 1, 5, 4),
 (3, 1, 5, 5),
 (3, 2, 0, 0),
 (3, 2, 0, 3),
 (3, 2, 0, 4),
 (3, 2, 0, 5),
 (3, 2, 1, 0),
 (3, 2, 1, 3),
 (3, 2, 1, 4),
 (3, 2, 1, 5),
 (3, 2, 2, 0),
 (3, 2, 2, 3),
 (3, 2, 2, 4),
 (3, 2, 2, 5),
 (3, 2, 5, 0),
 (3, 2, 5, 3),
 (3, 2, 5, 4),
 (3, 2, 5, 5),
 (3, 5, 0, 4),
 (3, 5, 1, 0),
 (3, 5, 1, 3),
 (3, 5, 1, 4),
 (3, 5, 1, 5),
 (3, 5, 2, 0),
 (3, 5, 2, 3),
 (3, 5, 2, 4),
 (3, 5, 5, 0),
 (3, 5, 5, 3),
 (3, 5, 5, 4),
 (4, 0, 0, 3),
 (4, 0, 0, 4),
 (4, 0, 0, 5),
 (4, 0, 1, 3),
 (4, 0, 1, 4),
 (4, 0, 1, 5),
 (4, 0, 2, 0),
 (4, 0, 2, 3),
 (4, 0, 2, 4),
 (4, 0, 2, 5),
 (4, 0, 5, 3),
 (4, 1, 0, 0),
 (4, 1, 0, 3),
 (4, 1, 0, 4),
 (4, 1, 0, 5),
 (4, 1, 1, 0),
 (4, 1, 1, 3),
 (4, 1, 1, 4),
 (4, 1, 1, 5),
 (4, 1, 2, 0),
 (4, 1, 2, 3),
 (4, 1, 2, 4),
 (4, 1, 2, 5),
 (4, 1, 5, 0),
 (4, 1, 5, 3),
 (4, 1, 5, 4),
 (4, 1, 5, 5),
 (4, 2, 0, 0),
 (4, 2, 0, 3),
 (4, 2, 0, 4),
 (4, 2, 0, 5),
 (4, 2, 1, 0),
 (4, 2, 1, 3),
 (4, 2, 1, 4),
 (4, 2, 1, 5),
 (4, 2, 2, 0),
 (4, 2, 2, 3),
 (4, 2, 2, 4),
 (4, 2, 2, 5),
 (4, 2, 5, 0),
 (4, 2, 5, 3),
 (4, 2, 5, 4),
 (4, 5, 0, 0),
 (4, 5, 0, 3),
 (4, 5, 0, 4),
 (4, 5, 0, 5),
 (4, 5, 1, 0),
 (4, 5, 1, 3),
 (4, 5, 1, 4),
 (4, 5, 1, 5),
 (4, 5, 2, 0),
 (4, 5, 2, 3),
 (4, 5, 2, 4),
 (4, 5, 2, 5),
 (4, 5, 5, 0),
 (4, 5, 5, 3),
 (4, 5, 5, 4),
 (5, 0, 0, 3),
 (5, 0, 0, 4),
 (5, 0, 0, 5),
 (5, 0, 1, 3),
 (5, 0, 1, 4),
 (5, 0, 1, 5),
 (5, 0, 2, 0),
 (5, 0, 2, 3),
 (5, 0, 2, 4),
 (5, 0, 2, 5),
 (5, 0, 5, 3),
 (5, 1, 0, 3),
 (5, 1, 0, 4),
 (5, 1, 0, 5),
 (5, 1, 1, 3),
 (5, 1, 1, 4),
 (5, 1, 1, 5),
 (5, 1, 2, 0),
 (5, 1, 2, 3),
 (5, 1, 2, 4),
 (5, 1, 2, 5),
 (5, 1, 5, 3),
 (5, 2, 0, 0),
 (5, 2, 0, 3),
 (5, 2, 0, 4),
 (5, 2, 0, 5),
 (5, 2, 1, 0),
 (5, 2, 1, 3),
 (5, 2, 1, 4),
 (5, 2, 1, 5),
 (5, 2, 2, 0),
 (5, 2, 2, 3),
 (5, 2, 2, 4),
 (5, 2, 2, 5),
 (5, 2, 5, 0),
 (5, 2, 5, 3),
 (5, 2, 5, 4),
 (5, 5, 0, 4),
 (5, 5, 1, 4),
 (5, 5, 2, 0),
 (5, 5, 2, 3),
 (5, 5, 2, 4)
])

conf = {"fill": "grey50", "tag": "oy", "outline": "black"}
def paint_cell(cell, x0, y0):
   if cell == 5:
      can.create_rectangle(x0, y0, x0+40, y0+40, **conf)
   elif cell == 4:
      can.create_polygon(x0, y0, x0, y0+40, x0+40, y0+40, **conf)
   elif cell == 3:
      can.create_polygon(x0+40, y0, x0, y0, x0+40, y0+40, **conf)
   elif cell == 2:
      can.create_polygon(x0+40, y0, x0, y0+40, x0+40, y0+40, **conf)
   elif cell == 1:
      can.create_polygon(x0, y0, x0+40, y0, x0, y0+40, **conf)

def next_quadruple(*args):
   try:
      quadruple = next(quadruples)
      lab.config(text = str(quadruple))
      for cell in can.find_withtag("oy"):
         can.delete(cell)
      for i in range(4):
         paint_cell(quadruple[i], i%2 * 40, i//2 * 40)
   except StopIteration:
      but.config(state = "disabled")

root = tkinter.Tk()
but = tkinter.Button(root, text = "Next", command = next_quadruple)
can = tkinter.Canvas(root, width = 80, height = 80, relief = "raised")
lab = tkinter.Label(root, text = "(_ ,_ ,_ ,_ )", font = ("Helvetica", 17))
but.grid(row = 0, column = 0)
can.grid(row = 0, column = 1)
lab.grid(row = 0, column = 2)
for i in (0,40,80):
   can.create_line(i,0,i,80, fill = "grey50")
   can.create_line(0,i,80,i, fill = "grey50")
root.mainloop()