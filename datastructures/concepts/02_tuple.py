"""
Tuple - an immutable, ordered sequence.
Used for fixed collections of values, multiple returns, and dict keys.
"""


def min_max(values):
    return min(values), max(values)        # returns a tuple


def main():
    point = (3, 4)
    print("tuple:", point)

    x, y = point                           # unpacking
    print("unpacked x, y:", x, y)

    try:
        point[0] = 10                      # tuples are immutable
    except TypeError as error:
        print("cannot modify tuple:", error)

    low, high = min_max([5, 2, 9, 1])
    print("min:", low, "max:", high)

    coordinates = {(0, 0): "origin", (1, 1): "diagonal"}  # tuple as dict key
    print("lookup (0, 0):", coordinates[(0, 0)])

    nested = (1, (2, 3), [4, 5])
    print("nested tuple:", nested)


if __name__ == "__main__":
    main()
