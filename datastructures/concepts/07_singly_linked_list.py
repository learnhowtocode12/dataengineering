"""
Singly Linked List - each node points only to the next node.
Insert/delete at head: O(1). Search/append: O(n).
"""


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class SinglyLinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def prepend(self, data):
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node

    def delete(self, data):
        current = self.head
        previous = None
        while current:
            if current.data == data:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                return True
            previous = current
            current = current.next
        return False

    def search(self, data):
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False

    def reverse(self):
        previous = None
        current = self.head
        while current:
            next_node = current.next
            current.next = previous
            previous = current
            current = next_node
        self.head = previous

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result


def main():
    ll = SinglyLinkedList()
    for value in [10, 20, 30]:
        ll.append(value)
    ll.prepend(5)
    print("list:", ll.to_list())

    ll.delete(20)
    print("after delete 20:", ll.to_list())

    print("search 30:", ll.search(30))
    print("search 99:", ll.search(99))

    ll.reverse()
    print("reversed:", ll.to_list())


if __name__ == "__main__":
    main()
