"""
Heap - a complete binary tree stored as an array, satisfying the heap
property (min-heap: parent <= children). Python's heapq module provides
a min-heap; a max-heap is simulated by negating values.
Priority Queue - built directly on top of a heap.
"""

import heapq


def demo_min_heap():
    print("--- Min-Heap (heapq) ---")
    heap = []
    for value in [5, 1, 8, 2, 9, 3]:
        heapq.heappush(heap, value)
    print("heap array form:", heap)

    sorted_values = []
    while heap:
        sorted_values.append(heapq.heappop(heap))   # pops smallest each time
    print("popped in order:", sorted_values)


def demo_max_heap():
    print("\n--- Max-Heap (negate values) ---")
    values = [5, 1, 8, 2, 9, 3]
    heap = [-v for v in values]
    heapq.heapify(heap)

    largest_three = [-heapq.heappop(heap) for _ in range(3)]
    print("3 largest values:", largest_three)


class PriorityQueue:
    """Lower priority number = served first. Ties broken by insertion order."""

    def __init__(self):
        self._heap = []
        self._counter = 0

    def push(self, item, priority):
        heapq.heappush(self._heap, (priority, self._counter, item))
        self._counter += 1

    def pop(self):
        priority, _, item = heapq.heappop(self._heap)
        return item, priority

    def is_empty(self):
        return len(self._heap) == 0


def demo_priority_queue():
    print("\n--- Priority Queue ---")
    pq = PriorityQueue()
    pq.push("low priority task", priority=5)
    pq.push("urgent task", priority=1)
    pq.push("medium task", priority=3)

    while not pq.is_empty():
        item, priority = pq.pop()
        print(f"priority {priority}: {item}")


if __name__ == "__main__":
    demo_min_heap()
    demo_max_heap()
    demo_priority_queue()
