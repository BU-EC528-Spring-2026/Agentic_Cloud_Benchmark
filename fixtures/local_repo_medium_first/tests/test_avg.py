# Tests for edge case with average fixture

import unittest
from samplepkg.avg import avg

class AverageTests(unittest.TestCase):
    def test_average_one(self) -> None:
        self.assertEqual(avg[5], 5.0)
    def test_average_list(self) -> None:
        self.assertEqual(avg([1,2,3]), 2.0)
    def test_average_empty(self) -> None:
        self.assertEqual(avg([]), 0.0)

if __name__ == "__main__":
    unittest.main()
