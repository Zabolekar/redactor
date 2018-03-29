# this file will generate an AS file with all the polyominoes of 8 or less cell

from redactor import polyominoes, field_to_contours, contours_to_AS

with open("Polyominoes_SquaresP4mm.as", "w") as f:
   f.write("{\n")
   for n in range(1, 9):
      f.write("{} : new <Figure>[\n".format(n))
      for field in polyominoes(n):
         f.write("new Figure(")
         f.write(contours_to_AS(field_to_contours(field)))
         f.write(" SquaresP4mm.The),\n")
      f.write("],\n\n")
   f.write("}")