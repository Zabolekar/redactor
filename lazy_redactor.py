from redactor import no_empty_rows_cols, connected, polyominoes, rotate, v_reflect, h_reflect, print_field, fill, field_to_contours
# TODO: use contours_to_AS

from tkinter import Tk, Toplevel, Canvas, Label, Spinbox, Button, IntVar, messagebox

if __name__ == "__main__":
   root = Tk()

   a = 20  # cell size
   w, h = 1000, 400  # canvas width and height
   # Scrollable canvas
   ca = Canvas(root, width=w, height=h)
   ca.bind("<ButtonPress-1>", lambda e: ca.scan_mark(e.x, e.y))
   ca.bind("<B1-Motion>", lambda e: ca.scan_dragto(e.x, e.y, gain=1))

   results = None # will turn into a polyominoes generator later
   def next_piece():
      global result
      ca.delete('all')
      ca.xview_moveto(0)
      ca.yview_moveto(0)
      n = tk_n.get() # TODO: not really, test
      try:
         result = next(results)
      except StopIteration:
         next_b.config(state="disabled")
         messagebox.showinfo("No more pieces", "No more pieces, try another number of cells")
         return
      for i, row in enumerate(result):
         for j, cell in enumerate(row):
            if cell:
               ca.create_rectangle(a + j * a, h//2 + i * a, a + j * a + a, h//2 + i * a + a, fill="grey50", tags="p")
               ca.tag_bind("p", '<ButtonPress-1>', combine(n))
               ca.tag_bind("p", '<Enter>', lambda e, tag="p":
                        [ca.itemconfig(i, fill="red")
                        for i in ca.find_withtag("p")])
               ca.tag_bind("p", '<Leave>', lambda e, tag="p":
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
   ca.grid(row=0, column=0, columnspan=3)
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
                  f.write('new <Vector.<Vertex>>[')
                  for contour in contours:
                     f.write('new <Vertex>[')
                     f.write(', '.join('new Vertex{}'.format(xy) for xy in contour))
                     f.write('],')
                  f.write("]\n")
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