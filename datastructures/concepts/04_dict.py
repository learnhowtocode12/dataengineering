"""
Dict - a built-in hash map of key -> value pairs.
Average O(1) insert/lookup/delete; insertion order preserved (Python 3.7+).
"""


def main():
    student = {"name": "Alice", "age": 21}
    student["grade"] = "A"                 # add new key
    student["age"] = 22                    # update existing key
    print("dict:", student)

    for key, value in student.items():
        print(f"{key}: {value}")

    print("get missing key with default:", student.get("major", "Undeclared"))

    del student["grade"]
    print("after delete 'grade':", student)

    counts = {}
    for word in ["a", "b", "a", "c", "b", "a"]:
        counts[word] = counts.get(word, 0) + 1     # frequency count pattern
    print("word counts:", counts)

    squares = {n: n * n for n in range(5)}          # dict comprehension
    print("squares dict:", squares)

    print("keys:", list(student.keys()))
    print("values:", list(student.values()))


if __name__ == "__main__":
    main()
