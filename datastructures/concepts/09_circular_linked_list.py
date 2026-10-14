"""
Circular Linked List - the last node points back to the head,
forming a loop. Useful for round-robin scheduling, cyclic buffers.
"""


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class CircularLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            new_node.next = self.head
            return
        current = self.head
        while current.next != self.head:
            current = current.next
        current.next = new_node
        new_node.next = self.head

    def to_list(self):
        result = []
        if self.head is None:
            return result
        current = self.head
        while True:
            result.append(current.data)
            current = current.next
            if current == self.head:
                break
        return result

    def traverse_n_times(self, n):
        """Demonstrates the circular property: walking past the tail wraps to head."""
        result = []
        if self.head is None:
            return result
        current = self.head
        for _ in range(n):
            result.append(current.data)
            current = current.next
        return result


def main():
    cll = CircularLinkedList()
    for value in [1, 2, 3, 4]:
        cll.append(value)
    print("list:", cll.to_list())
    print("traverse 7 steps (wraps around):", cll.traverse_n_times(7))


if __name__ == "__main__":
    main()
