# Simple average fuction with a seeded defect

def avg(values: list) -> float:
    return sum(values)/len(values) # bug here: crashes on empty list
