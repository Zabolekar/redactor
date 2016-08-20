import unittest
import profile
from redactor import polyominoes

class TestRedactor(unittest.TestCase):
   def test_nfree(self):
      for i, should_be in enumerate([1,1,2,5,12,35,108,369], 1):
         actually_is = len(list(polyominoes(i)))
         print("{} cells, {} free polyominoes returned, should be {}".format(i, actually_is, should_be))
         self.assertTrue(actually_is == should_be)
   
if __name__ == '__main__':
   unittest.main()
   #profile.run("list(polyominoes(8))")