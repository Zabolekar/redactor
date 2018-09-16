from timeit import timeit
from redactor import polyominoes

for i in range(1, 10):
   elapsed = timeit("list(polyominoes(i))", number=1, globals=globals())
   print(f"n = {i}, t = {elapsed:0.6f} s")
