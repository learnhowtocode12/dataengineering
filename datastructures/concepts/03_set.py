"""
Set - an unordered collection of unique, hashable elements.
Backed by a hash table: average O(1) add/remove/lookup.
"""


def main():
    a = {1, 2, 3, 4}
    b = {3, 4, 5, 6}

    print("a:", a)
    print("b:", b)
    print("union a | b:", a | b)
    print("intersection a & b:", a & b)
    print("difference a - b:", a - b)
    print("symmetric difference a ^ b:", a ^ b)

    a.add(10)
    a.discard(1)                 # remove without raising if missing
    print("after add(10), discard(1):", a)

    print("is {3, 4} subset of b?", {3, 4} <= b)

    duplicates = [1, 2, 2, 3, 3, 3]
    unique_values = set(duplicates)
    print("de-duplicated:", unique_values)

    frozen = frozenset([1, 2, 3])        # immutable, hashable set
    print("frozenset (hashable):", frozen)


if __name__ == "__main__":
    main()
