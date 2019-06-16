from tkinter import Tk, Toplevel, Canvas, Label, Spinbox, Button, IntVar, Event, filedialog, messagebox
from typing import Any, Callable, Dict, List, Optional, Union
from copy import deepcopy
from warnings import warn
from io import StringIO
from polyominoes_types import Cell, Contours, Field, PositionedCell, Transformation
from polyominoes import polyominoes
from field_to_contours import field_to_contours

from polyominoes import EAGER

######################################################
##### Neither generation-related nor GUI-related #####
######################################################

def print_field(field: Field) -> None:
   # cutting empty rows
   for i, row in enumerate(field):
      if any(cell is not Cell.EMPTY for cell in row):
         break
   for j, row in reversed(list(enumerate(field, 1))):
      if any(cell is not Cell.EMPTY for cell in row):
         break
   # TODO: cut empty columns, too
   print("\n".join("".join('#' if cell is not Cell.EMPTY else ' ' for cell in row) for row in field[i:j]))
   print("\n\n")

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

Callback = Callable[[Event], None]

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
   figures: Dict[str, List[PositionedCell]] = {}

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
                        figures[tag].append(PositionedCell(zn + j, i))
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
                                              title="Append figure to file",
                                              confirmoverwrite=False)
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
                        figures[selected] = [PositionedCell(-o.y, o.x) for o in figures[selected]]
                     elif kind == Transformation.REFLECT_OVER_VERTICAL_AXIS:
                        figures[selected] = [PositionedCell(-o.x, o.y) for o in figures[selected]]
                     elif kind == Transformation.REFLECT_OVER_HORIZONTAL_AXIS:
                        figures[selected] = [PositionedCell(o.x, -o.y) for o in figures[selected]]
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
