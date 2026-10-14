"""
AVL Tree - a self-balancing BST. After every insert, rotations restore
the invariant that left/right subtree heights differ by at most 1,
guaranteeing O(log n) height and operations.
"""


class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.height = 1


class AVLTree:
    def __init__(self):
        self.root = None

    def _height(self, node):
        return node.height if node else 0

    def _balance_factor(self, node):
        return self._height(node.left) - self._height(node.right) if node else 0

    def _update_height(self, node):
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _rotate_right(self, y):
        x = y.left
        y.left = x.right
        x.right = y
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        y.left = x
        self._update_height(x)
        self._update_height(y)
        return y

    def insert(self, value):
        self.root = self._insert(self.root, value)

    def _insert(self, node, value):
        if node is None:
            return TreeNode(value)
        if value < node.value:
            node.left = self._insert(node.left, value)
        else:
            node.right = self._insert(node.right, value)

        self._update_height(node)
        balance = self._balance_factor(node)

        if balance > 1 and value < node.left.value:        # left-left case
            return self._rotate_right(node)
        if balance < -1 and value > node.right.value:      # right-right case
            return self._rotate_left(node)
        if balance > 1 and value > node.left.value:         # left-right case
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1 and value < node.right.value:       # right-left case
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def inorder(self):
        result = []
        self._inorder(self.root, result)
        return result

    def _inorder(self, node, result):
        if node:
            self._inorder(node.left, result)
            result.append(node.value)
            self._inorder(node.right, result)


def main():
    avl = AVLTree()
    # Inserting in increasing order would unbalance a plain BST into a line;
    # the AVL tree keeps itself balanced automatically.
    for value in [10, 20, 30, 40, 50, 25]:
        avl.insert(value)

    print("inorder (sorted):", avl.inorder())
    print("root value after balancing:", avl.root.value)
    print("tree height:", avl.root.height)


if __name__ == "__main__":
    main()
