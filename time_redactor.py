from timeit import timeit
from redactor import polyominoes

for i in range(1, 9):
   elapsed = timeit("list(polyominoes(i))", number=1, globals=globals())
   print(f"n = {i}, t = {elapsed:0.6f} s")

# n = 9 would require ~277 s, which is hardly acceptable
