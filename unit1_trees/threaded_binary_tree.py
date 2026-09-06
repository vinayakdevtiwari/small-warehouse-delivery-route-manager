"""Right-threaded binary search tree (DSA learning implementation)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

T = TypeVar("T")


@dataclass
class ThreadedNode(Generic[T]):
    value: T
    left: Optional["ThreadedNode[T]"] = None
    right: Optional["ThreadedNode[T]"] = None
    right_is_thread: bool = False


class ThreadedBinarySearchTree(Generic[T]):
    """BST whose absent right links point to inorder successors.

    Inorder traversal is O(n) time and O(1) auxiliary space. Search and insert
    are O(h) (O(log n) balanced average, O(n) worst case). Deletion is omitted
    deliberately because maintaining threads during all delete cases is a
    separate advanced operation, not needed by this project.
    """

    def __init__(self) -> None:
        self.root: Optional[ThreadedNode[T]] = None

    def insert(self, value: T) -> None:
        """Insert a unique value while preserving right threads: O(h)."""
        if self.root is None:
            self.root = ThreadedNode(value)
            return
        current = self.root
        while True:
            if value == current.value:
                raise KeyError(f"duplicate value: {value!r}")
            if value < current.value:
                if current.left is None:
                    current.left = ThreadedNode(value, right=current, right_is_thread=True)
                    return
                current = current.left
            else:
                if current.right is None or current.right_is_thread:
                    successor = current.right if current.right_is_thread else None
                    current.right = ThreadedNode(value, right=successor, right_is_thread=successor is not None)
                    current.right_is_thread = False
                    return
                current = current.right

    def contains(self, value: T) -> bool:
        """Search by BST order: O(h)."""
        current = self.root
        while current is not None:
            if value == current.value:
                return True
            if value < current.value:
                current = current.left
            else:
                current = None if current.right_is_thread else current.right
        return False

    def inorder(self) -> Iterator[T]:
        """Traverse inorder without recursion or a stack: O(n), O(1) extra space."""
        current = self.root
        if current is None:
            return
        while current.left is not None:
            current = current.left
        while current is not None:
            yield current.value
            if current.right_is_thread:
                current = current.right
            else:
                current = current.right
                while current is not None and current.left is not None:
                    current = current.left


if __name__ == "__main__":
    tree = ThreadedBinarySearchTree[int]()
    for location_code in (50, 30, 70, 20, 40, 60, 80):
        tree.insert(location_code)
    print("Threaded inorder:", list(tree.inorder()))
    print("Contains 60:", tree.contains(60))
