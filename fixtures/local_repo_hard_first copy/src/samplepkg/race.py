# Simple shared couter with a simulated race condiition
import threading

class Counter:
    def __init__(self):
        self.value = 0
        self._lock = threading.Lock()

    def increment(self):
        current = self.value # bug here: r + w not atomic
        self.value = current + 1 # bug here: lock not acquired