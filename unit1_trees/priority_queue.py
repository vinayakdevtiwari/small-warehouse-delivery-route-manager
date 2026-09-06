"""Stable priority queue built on the reusable BinaryHeap."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar

try:
    from .binary_heap import BinaryHeap
except ImportError:  # Allows direct execution from this folder too.
    from binary_heap import BinaryHeap

T = TypeVar("T")


@dataclass(frozen=True)
class QueueEntry(Generic[T]):
    priority: int
    item: T


class PriorityQueue(Generic[T]):
    """Stable min-priority queue: lower numeric priority is served first.

    enqueue and dequeue are O(log n); peek is O(1). Equal-priority entries are
    served in arrival order, which is useful for fair delivery dispatching.
    """

    def __init__(self) -> None:
        self._heap: BinaryHeap[tuple[int, int, T]] = BinaryHeap(kind="min")
        self._next_sequence = 0

    def __len__(self) -> int:
        return len(self._heap)

    def is_empty(self) -> bool:
        return self._heap.is_empty()

    def enqueue(self, item: T, priority: int) -> None:
        """Add an item with an integer priority: O(log n)."""
        if not isinstance(priority, int):
            raise TypeError("priority must be an integer")
        self._heap.push((priority, self._next_sequence, item))
        self._next_sequence += 1

    def dequeue(self) -> QueueEntry[T]:
        """Remove and return the next item to process: O(log n)."""
        priority, _, item = self._heap.pop()
        return QueueEntry(priority, item)

    def peek(self) -> QueueEntry[T]:
        """Inspect the next item without removing it: O(1)."""
        priority, _, item = self._heap.peek()
        return QueueEntry(priority, item)


if __name__ == "__main__":
    orders: PriorityQueue[str] = PriorityQueue()
    orders.enqueue("ORD-104: medicine delivery", priority=1)
    orders.enqueue("ORD-105: regular parcel", priority=3)
    orders.enqueue("ORD-106: fragile item", priority=2)
    orders.enqueue("ORD-107: second regular parcel", priority=3)
    print("Next order:", orders.peek())
    while not orders.is_empty():
        print("Dispatch:", orders.dequeue())
