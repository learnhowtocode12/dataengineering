"""
Trie (prefix tree) - a tree where each path from the root spells out a
string. Efficient for prefix search, autocomplete, and dictionary lookups:
O(m) time for insert/search, where m is the word length.
"""


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            node = node.children.setdefault(char, TrieNode())
        node.is_end_of_word = True

    def search(self, word):
        node = self._find_node(word)
        return node is not None and node.is_end_of_word

    def starts_with(self, prefix):
        return self._find_node(prefix) is not None

    def _find_node(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def words_with_prefix(self, prefix):
        node = self._find_node(prefix)
        if node is None:
            return []
        results = []
        self._collect(node, prefix, results)
        return results

    def _collect(self, node, path, results):
        if node.is_end_of_word:
            results.append(path)
        for char, child in node.children.items():
            self._collect(child, path + char, results)


def main():
    trie = Trie()
    for word in ["cat", "car", "card", "care", "dog"]:
        trie.insert(word)

    print("search 'car':", trie.search("car"))
    print("search 'ca':", trie.search("ca"))
    print("starts_with 'ca':", trie.starts_with("ca"))
    print("words with prefix 'car':", trie.words_with_prefix("car"))
    print("words with prefix 'do':", trie.words_with_prefix("do"))


if __name__ == "__main__":
    main()
