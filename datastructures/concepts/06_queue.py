"""
Queue - FIFO (First In, First Out) structure.
Implemented with collections.deque for O(1) enqueue/dequeue at both ends.
"""

from collections import deque


class Queue:
    def __init__(self):
        self._items = deque()

    def enqueue(self, item):
        self._items.append(item)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        return self._items.popleft()

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)


class Deque:
    """Double-ended queue: can add/remove from both front and back."""

    def __init__(self):
        self._items = deque()

    def add_front(self, item):
        self._items.appendleft(item)

    def add_rear(self, item):
        self._items.append(item)

    def remove_front(self):
        return self._items.popleft()

    def remove_rear(self):
        return self._items.pop()


def main():
    queue = Queue()
    for value in [1, 2, 3]:
        queue.enqueue(value)
    while not queue.is_empty():
        print("dequeue:", queue.dequeue())

    dq = Deque()
    dq.add_rear(1)
    dq.add_front(0)
    dq.add_rear(2)
    print("remove_front:", dq.remove_front())
    print("remove_rear:", dq.remove_rear())


if __name__ == "__main__":
    main()
