# Tests for shared counter with race condition
import unittest
from samplepkg.race import Counter
import threading


class AverageTests(unittest.TestCase):
    def test_single_threaded(self) -> None:
        c = Counter()
        for _ in range(100):
            c.increment()
        self.assertEqual(c.value, 100)

    def test_concurrent_increments(self) -> None:
       # run concurrent threads
        NUM_THREADS = 50
        INCREMENTS_PER_THREAD = 100

        c = Counter()
        threads = [
            threading.Thread(target=lambda: [c.increment() for _ in range(INCREMENTS_PER_THREAD)])
            for _ in range(NUM_THREADS)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        expected = NUM_THREADS * INCREMENTS_PER_THREAD
        self.assertEqual(c.value, expected)

if __name__ == "__main__":
    unittest.main()
