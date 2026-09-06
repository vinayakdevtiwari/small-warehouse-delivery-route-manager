"""Self-balancing AVL key/value tree (DSA learning implementation)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class AVLNode(Generic[K, V]):
    key: K
    value: V
    height: int = 1
    left: Optional["AVLNode[K, V]"] = None
    right: Optional["AVLNode[K, V]"] = None


class AVLTree(Generic[K, V]):
    """Ordered map that rebalances after insertion and deletion.

    Search, insert, update, and delete are O(log n) worst case. Inorder
    traversal is O(n). Rotations take O(1).
    """

    def __init__(self) -> None:
        self.root: Optional[AVLNode[K, V]] = None
        self.size = 0

    @staticmethod
    def _height(node: Optional[AVLNode[K, V]]) -> int:
        return node.height if node is not None else 0

    def _refresh_height(self, node: AVLNode[K, V]) -> None:
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _balance(self, node: AVLNode[K, V]) -> int:
        return self._height(node.left) - self._height(node.right)

    def _rotate_right(self, parent: AVLNode[K, V]) -> AVLNode[K, V]:
        pivot = parent.left
        assert pivot is not None
        middle = pivot.right
        pivot.right = parent
        parent.left = middle
        self._refresh_height(parent)
        self._refresh_height(pivot)
        return pivot

    def _rotate_left(self, parent: AVLNode[K, V]) -> AVLNode[K, V]:
        pivot = parent.right
        assert pivot is not None
        middle = pivot.left
        pivot.left = parent
        parent.right = middle
        self._refresh_height(parent)
        self._refresh_height(pivot)
        return pivot

    def _rebalance(self, node: AVLNode[K, V]) -> AVLNode[K, V]:
        self._refresh_height(node)
        balance = self._balance(node)
        if balance > 1:
            if self._balance(node.left) < 0:
                assert node.left is not None
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if balance < -1:
            if self._balance(node.right) > 0:
                assert node.right is not None
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def insert(self, key: K, value: V) -> None:
        """Insert a unique key/value pair: O(log n)."""
        def add(node: Optional[AVLNode[K, V]]) -> AVLNode[K, V]:
            if node is None:
                self.size += 1
                return AVLNode(key, value)
            if key == node.key:
                raise KeyError(f"key already exists: {key!r}")
            if key < node.key:
                node.left = add(node.left)
            else:
                node.right = add(node.right)
            return self._rebalance(node)
        self.root = add(self.root)

    def search(self, key: K) -> V:
        """Look up a key: O(log n)."""
        node = self.root
        while node is not None:
            if key == node.key:
                return node.value
            node = node.left if key < node.key else node.right
        raise KeyError(f"key not found: {key!r}")

    def update(self, key: K, value: V) -> None:
        """Replace the value for an existing key: O(log n)."""
        node = self.root
        while node is not None:
            if key == node.key:
                node.value = value
                return
            node = node.left if key < node.key else node.right
        raise KeyError(f"key not found: {key!r}")

    def delete(self, key: K) -> None:
        """Remove a key and rebalance the path to root: O(log n)."""
        def remove(node: Optional[AVLNode[K, V]], target: K) -> tuple[Optional[AVLNode[K, V]], bool]:
            if node is None:
                return None, False
            if target < node.key:
                node.left, deleted = remove(node.left, target)
            elif target > node.key:
                node.right, deleted = remove(node.right, target)
            else:
                deleted = True
                if node.left is None:
                    return node.right, True
                if node.right is None:
                    return node.left, True
                successor = node.right
                while successor.left is not None:
                    successor = successor.left
                node.key, node.value = successor.key, successor.value
                node.right, _ = remove(node.right, successor.key)
            return self._rebalance(node), deleted
        self.root, deleted = remove(self.root, key)
        if not deleted:
            raise KeyError(f"key not found: {key!r}")
        self.size -= 1

    def inorder_items(self) -> Iterator[tuple[K, V]]:
        """Yield records ordered by key: O(n)."""
        def walk(node: Optional[AVLNode[K, V]]) -> Iterator[tuple[K, V]]:
            if node is not None:
                yield from walk(node.left)
                yield (node.key, node.value)
                yield from walk(node.right)
        yield from walk(self.root)


if __name__ == "__main__":
    products: AVLTree[int, str] = AVLTree()
    for product_id in (30, 20, 10, 25, 28, 40):
        products.insert(product_id, f"Product-{product_id}")
    products.delete(20)
    print("Balanced inventory keys:", list(products.inorder_items()))
    print("Product 28:", products.search(28))
