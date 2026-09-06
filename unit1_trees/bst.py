"""Key/value Binary Search Tree suitable for a small product index."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class BSTNode(Generic[K, V]):
    key: K
    value: V
    left: Optional["BSTNode[K, V]"] = None
    right: Optional["BSTNode[K, V]"] = None


class BinarySearchTree(Generic[K, V]):
    """Unbalanced ordered map.

    Search, insert, update, and delete take O(h), where h is tree height:
    O(log n) for a reasonably balanced tree and O(n) in the worst case.
    Traversal is O(n). Use `AVLTree` if worst-case O(log n) is necessary.
    """

    def __init__(self) -> None:
        self.root: Optional[BSTNode[K, V]] = None
        self.size = 0

    def insert(self, key: K, value: V) -> None:
        """Insert a new key/value pair; raises KeyError for an existing key."""
        if self.root is None:
            self.root = BSTNode(key, value)
            self.size = 1
            return
        current = self.root
        while True:
            if key == current.key:
                raise KeyError(f"key already exists: {key!r}")
            if key < current.key:
                if current.left is None:
                    current.left = BSTNode(key, value)
                    self.size += 1
                    return
                current = current.left
            else:
                if current.right is None:
                    current.right = BSTNode(key, value)
                    self.size += 1
                    return
                current = current.right

    def search(self, key: K) -> V:
        """Return the matching value, or raise KeyError: O(h)."""
        current = self.root
        while current is not None:
            if key == current.key:
                return current.value
            current = current.left if key < current.key else current.right
        raise KeyError(f"key not found: {key!r}")

    def get(self, key: K, default: Optional[V] = None) -> Optional[V]:
        """Return a value or default when absent: O(h)."""
        try:
            return self.search(key)
        except KeyError:
            return default

    def update(self, key: K, value: V) -> None:
        """Replace the value for an existing key: O(h)."""
        current = self.root
        while current is not None:
            if key == current.key:
                current.value = value
                return
            current = current.left if key < current.key else current.right
        raise KeyError(f"key not found: {key!r}")

    def delete(self, key: K) -> None:
        """Delete a key, including the zero/one/two-child cases: O(h)."""
        self.root, deleted = self._delete(self.root, key)
        if not deleted:
            raise KeyError(f"key not found: {key!r}")
        self.size -= 1

    def _delete(self, node: Optional[BSTNode[K, V]], key: K) -> tuple[Optional[BSTNode[K, V]], bool]:
        if node is None:
            return None, False
        if key < node.key:
            node.left, deleted = self._delete(node.left, key)
            return node, deleted
        if key > node.key:
            node.right, deleted = self._delete(node.right, key)
            return node, deleted
        if node.left is None:
            return node.right, True
        if node.right is None:
            return node.left, True
        successor = self._minimum(node.right)
        node.key, node.value = successor.key, successor.value
        node.right, _ = self._delete(node.right, successor.key)
        return node, True

    @staticmethod
    def _minimum(node: BSTNode[K, V]) -> BSTNode[K, V]:
        while node.left is not None:
            node = node.left
        return node

    def inorder_items(self) -> Iterator[tuple[K, V]]:
        """Yield sorted (key, value) pairs: O(n)."""
        def walk(node: Optional[BSTNode[K, V]]) -> Iterator[tuple[K, V]]:
            if node is not None:
                yield from walk(node.left)
                yield (node.key, node.value)
                yield from walk(node.right)
        yield from walk(self.root)

    def __contains__(self, key: object) -> bool:
        try:
            self.search(key)  # type: ignore[arg-type]
            return True
        except (KeyError, TypeError):
            return False


if __name__ == "__main__":
    products: BinarySearchTree[int, dict[str, object]] = BinarySearchTree()
    for product_id, product in [
        (104, {"name": "Packing tape", "stock": 18}),
        (101, {"name": "Box", "stock": 42}),
        (108, {"name": "Label roll", "stock": 9}),
        (106, {"name": "Bubble wrap", "stock": 25}),
    ]:
        products.insert(product_id, product)
    print("Product 106:", products.search(106))
    products.update(108, {"name": "Label roll", "stock": 24})
    products.delete(104)
    print("Sorted inventory:", list(products.inorder_items()))
