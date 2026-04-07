# Test for range sum fixture

import unittest
from samplepkg.range_sum import range_sum

class RangeSumTests(unittest.TestCase):
    def test_zero(self) -> None:
        self.assertEqual(range_sum(0), 0)
    def test_one(self) -> None:
        self.assertEqual(range_sum(1), 1)
    def test_large(self) -> None:
        self.assertEqual(range_sum(10), 55)

if __name__ == "__main__":
    unittest.main()
