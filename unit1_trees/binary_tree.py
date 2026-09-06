"""A general binary tree using level-order insertion (learning implementation)."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


@dataclass
class BinaryTreeNode(Generic[T]):
    value: T
    left: Optional["BinaryTreeNode[T]"] = None
    right: Optional["BinaryTreeNode[T]"] = None


class BinaryTree(Generic[T]):
    """Complete-style binary tree; unlike a BST it does not order values.

    insert/search/traversal are O(n) in the worst case. Level-order insertion
    is O(n), because it finds the first available child position.
    """

    def __init__(self) -> None:
        self.root: Optional[BinaryTreeNode[T]] = None

    def insert(self, value: T) -> None:
        """Insert at the first open position in level order: O(n)."""
        node = BinaryTreeNode(value)
        if self.root is None:
            self.root = node
            return
        queue: deque[BinaryTreeNode[T]] = deque([self.root])
        while queue:
            current = queue.popleft()
            if current.left is None:
                current.left = node
                return
            if current.right is None:
                current.right = node
                return
            queue.extend((current.left, current.right))

    def contains(self, value: T) -> bool:
        """Return whether a value exists, using breadth-first search: O(n)."""
        return any(item == value for item in self.level_order())

    def level_order(self) -> Iterator[T]:
        """Yield values breadth first: O(n) time and O(n) auxiliary space."""
        if self.root is None:
            return
        queue: deque[BinaryTreeNode[T]] = deque([self.root])
        while queue:
            current = queue.popleft()
            yield current.value
            if current.left is not None:
                queue.append(current.left)
            if current.right is not None:
                queue.append(current.right)

    def inorder(self) -> Iterator[T]:
        """Yield left, node, right recursively: O(n)."""
        def walk(node: Optional[BinaryTreeNode[T]]) -> Iterator[T]:
            if node is not None:
                yield from walk(node.left)
                yield node.value
                yield from walk(node.right)
        yield from walk(self.root)

    def preorder(self) -> Iterator[T]:
        """Yield node, left, right recursively: O(n)."""
        def walk(node: Optional[BinaryTreeNode[T]]) -> Iterator[T]:
            if node is not None:
                yield node.value
                yield from walk(node.left)
                yield from walk(node.right)
        yield from walk(self.root)

    def postorder(self) -> Iterator[T]:
        """Yield left, right, node recursively: O(n)."""
        def walk(node: Optional[BinaryTreeNode[T]]) -> Iterator[T]:
            if node is not None:
                yield from walk(node.left)
                yield from walk(node.right)
                yield node.value
        yield from walk(self.root)


if __name__ == "__main__":
    tree = BinaryTree[str]()
    for section in ("Receiving", "Storage", "Packing", "Dispatch", "Returns"):
        tree.insert(section)
    print("Level order:", list(tree.level_order()))
    print("Preorder:", list(tree.preorder()))
    print("Contains Packing:", tree.contains("Packing"))
