from redactor import polyominoes

def test_n_free():
   for i, should_be in enumerate([1, 1, 2, 5, 12, 35, 108, 369], 1):
      actually_is = len(list(polyominoes(i)))
      assert actually_is == should_be
