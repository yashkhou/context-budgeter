import unittest,sys; sys.path.insert(0,'src')
from context_budgeter.core import *
class T(unittest.TestCase):
 def test_estimate(self): self.assertEqual(estimate('1234'),1)
 def test_duplicate(self): self.assertTrue(duplicates([{'id':'a','text':'one two three'},{'id':'b','text':'one two three'}]))
 def test_collision(self): self.assertEqual(collisions([{'text':'allow network'},{'text':'deny network'}])[0]['subject'],'network')
 def test_budget(self): self.assertLessEqual(allocate([{'id':'a','text':'x'*40,'priority':1}],5)['used'],5)
