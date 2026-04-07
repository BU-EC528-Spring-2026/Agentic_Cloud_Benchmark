# Running sum function with a seeded defect

def range_sum(n: int) -> int:
    total = 0
    for i in range(n): # bug here: should be range(1, n+1)
        total += i
    return total