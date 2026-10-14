"""
Binary Tree - each node has at most two children (left, right).
No ordering guarantee (unlike a BST). Shown with the three classic
depth-first traversals plus breadth-first (level order) traversal.
"""

from collections import deque


class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


def preorder(node, result):
    if node:
        result.append(node.value)
        preorder(node.left, result)
        preorder(node.right, result)


def inorder(node, result):
    if node:
        inorder(node.left, result)
        result.append(node.value)
        inorder(node.right, result)


def postorder(node, result):
    if node:
        postorder(node.left, result)
        postorder(node.right, result)
        result.append(node.value)


def level_order(root):
    result = []
    if root is None:
        return result
    queue = deque([root])
    while queue:
        node = queue.popleft()
        result.append(node.value)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return result


def height(node):
    if node is None:
        return -1
    return 1 + max(height(node.left), height(node.right))


def build_sample_tree():
    #        1
    #      /   \
    #     2     3
    #    / \   / \
    #   4   5 6   7
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)
    root.right.left = TreeNode(6)
    root.right.right = TreeNode(7)
    return root


def main():
    root = build_sample_tree()

    preorder_result = []
    preorder(root, preorder_result)
    print("preorder:", preorder_result)

    inorder_result = []
    inorder(root, inorder_result)
    print("inorder:", inorder_result)

    postorder_result = []
    postorder(root, postorder_result)
    print("postorder:", postorder_result)

    print("level order (BFS):", level_order(root))
    print("height:", height(root))


if __name__ == "__main__":
    main()
