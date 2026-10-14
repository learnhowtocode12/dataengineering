"""
List - a mutable, ordered, resizable sequence (dynamic array).
Common ops: index access, append, insert, remove, slice, sort, comprehension.
"""


def main():
    numbers = [5, 3, 8, 1, 9]
    print("original:", numbers)

    numbers.append(12)                 # add to end -> O(1) amortized
    numbers.insert(0, 100)              # insert at index -> O(n)
    numbers.remove(3)                   # remove first matching value -> O(n)
    print("after append/insert/remove:", numbers)

    print("index access numbers[2]:", numbers[2])
    print("slice numbers[1:4]:", numbers[1:4])
    print("reversed:", numbers[::-1])

    numbers.sort()
    print("sorted:", numbers)

    squares = [n * n for n in numbers if n % 2 == 0]
    print("squares of even numbers:", squares)

    print("length:", len(numbers))
    print("contains 9?", 9 in numbers)


if __name__ == "__main__":
    main()
