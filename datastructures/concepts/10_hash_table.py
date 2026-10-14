"""
Hash Table - custom implementation from scratch using separate chaining
to resolve collisions. Python's dict does this internally with open addressing;
this shows the underlying concept explicitly.
"""


class HashTable:
    def __init__(self, capacity=8):
        self.capacity = capacity
        self.size = 0
        self.buckets = [[] for _ in range(capacity)]   # each bucket is a list of (key, value)

    def _hash(self, key):
        return hash(key) % self.capacity

    def put(self, key, value):
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                bucket[i] = (key, value)        # update existing key
                return
        bucket.append((key, value))
        self.size += 1
        if self.size / self.capacity > 0.75:    # resize when load factor too high
            self._resize()

    def get(self, key):
        index = self._hash(key)
        for existing_key, value in self.buckets[index]:
            if existing_key == key:
                return value
        raise KeyError(key)

    def remove(self, key):
        index = self._hash(key)
        bucket = self.buckets[index]
        for i, (existing_key, _) in enumerate(bucket):
            if existing_key == key:
                del bucket[i]
                self.size -= 1
                return True
        return False

    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)

    def __contains__(self, key):
        index = self._hash(key)
        return any(existing_key == key for existing_key, _ in self.buckets[index])

    def items(self):
        for bucket in self.buckets:
            for key, value in bucket:
                yield key, value


def main():
    table = HashTable(capacity=4)
    table.put("name", "Alice")
    table.put("age", 21)
    table.put("city", "Chennai")
    table.put("country", "India")     # triggers a resize (load factor > 0.75)

    print("get 'name':", table.get("name"))
    print("'age' in table:", "age" in table)

    table.remove("age")
    print("'age' in table after remove:", "age" in table)

    print("all items:")
    for key, value in table.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
