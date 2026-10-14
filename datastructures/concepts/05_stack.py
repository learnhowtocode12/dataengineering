"""
Stack - LIFO (Last In, First Out) structure.
Operations: push, pop, peek - all O(1) using a Python list as backing storage.
"""


class Stack:
    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)


def is_balanced(expression):
    """Classic stack use case: matching parentheses/brackets/braces."""
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = Stack()
    for char in expression:
        if char in "([{":
            stack.push(char)
        elif char in ")]}":
            if stack.is_empty() or stack.pop() != pairs[char]:
                return False
    return stack.is_empty()


def main():
    stack = Stack()
    for value in [1, 2, 3]:
        stack.push(value)
    print("peek:", stack.peek())
    while not stack.is_empty():
        print("pop:", stack.pop())

    print("is_balanced('(a[b]{c})'):", is_balanced("(a[b]{c})"))
    print("is_balanced('(a[b)c]'):", is_balanced("(a[b)c]"))


if __name__ == "__main__":
    main()
