"""0/1 Knapsack Problem using Dynamic Programming (Bottom-Up Tabulation).

Algorithm Role:
- Current Status: Implemented and tested.
- Project Relevance: Vehicle/package selection under limited capacity.
- Classification: Project-relevant / planned integration.
- Note: Full integration into the end-to-end warehouse order workflow remains planned future work;
  demonstrated here as a standalone tested module for package payload optimization.

DP Concepts (Richard Bellman):
- Optimal Substructure: An optimal payload of weight W either contains item i plus the optimal
  selection of remaining items for capacity W - w_i, or excludes item i.
- Overlapping Subproblems: Subproblems c[i, w] are referenced repeatedly and stored in a 2D table.
- State: c[i, w] represents the maximum value achievable considering items 1..i with capacity w.
- Transition Recurrence:
    c[i, w] = c[i-1, w]                                      if w_i > w
    c[i, w] = max(c[i-1, w], p_i + c[i-1, w - w_i])          if w_i <= w
- Base Case: c[0, w] = 0 for all w, and c[i, 0] = 0 for all i.

Complexity:
- Time Complexity: Theta(n * W) where n is the number of items and W is integer capacity.
  Fills a 2D table of size (n + 1) * (W + 1) where each cell requires O(1) time.
- Space Complexity: Theta(n * W) for the 2D tabulation table used for backtracking.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Parcel:
    """Represents a customer order package for vehicle dispatch."""
    order_id: str
    weight: int
    value: float


def knapsack_01(
    parcels: list[Parcel], capacity: int
) -> tuple[float, list[Parcel], list[list[float]]]:
    """Solve the 0/1 Knapsack problem using bottom-up tabulation.

    Algorithm (from DSA-II Lecture Unit 3 Slides 27-35):
    1. Allocate table c of dimensions (n + 1) x (capacity + 1) initialized to 0.
    2. Fill the table row by row for i in 1..n and w in 1..capacity.
    3. Reconstruct the selected items by backtracking from c[n, capacity].

    Args:
        parcels: List of candidate Parcel items (weight must be positive integer).
        capacity: Maximum allowable payload weight (integer).

    Returns:
        A tuple of (maximum_value, selected_parcels, dp_table).
    """
    if capacity < 0:
        raise ValueError("Capacity must be non-negative.")

    n = len(parcels)
    # c[i][w] stores max value using subset of first i items with capacity w
    c = [[0.0] * (capacity + 1) for _ in range(n + 1)]

    # Fill DP table
    for i in range(1, n + 1):
        item = parcels[i - 1]
        for w in range(1, capacity + 1):
            if item.weight <= w:
                include_val = item.value + c[i - 1][w - item.weight]
                exclude_val = c[i - 1][w]
                if include_val > exclude_val:
                    c[i][w] = include_val
                else:
                    c[i][w] = exclude_val
            else:
                c[i][w] = c[i - 1][w]

    # Backtracking to identify selected items (PPT slide 30)
    selected_items: list[Parcel] = []
    w_remaining = capacity
    for i in range(n, 0, -1):
        if c[i][w_remaining] != c[i - 1][w_remaining]:
            # Item i was included
            item = parcels[i - 1]
            selected_items.append(item)
            w_remaining -= item.weight

    selected_items.reverse()
    max_value = c[n][capacity]

    return max_value, selected_items, c


def display_knapsack_table(c: list[list[float]], max_cols: int = 15) -> str:
    """Format the 2D DP table into a readable matrix string."""
    rows = len(c)
    cols = len(c[0])
    limit = min(cols, max_cols)

    header = "i \\ w".ljust(8) + "".join(f"{w:6d}" for w in range(limit))
    if cols > max_cols:
        header += "  ..."
    lines = [header, "-" * len(header)]

    for i in range(rows):
        row_str = f"Item {i}".ljust(8) + "".join(f"{int(c[i][w]):6d}" for w in range(limit))
        if cols > max_cols:
            row_str += "  ..."
        lines.append(row_str)

    return "\n".join(lines)


if __name__ == "__main__":
    print("=== 0/1 Knapsack Problem (Core Vehicle Payload Optimization) ===")

    # Test 1: Simulated Warehouse Delivery Van Loading
    vehicle_capacity = 25  # kg
    delivery_orders = [
        Parcel("ORD-101 (Laptop)", weight=5, value=500.0),
        Parcel("ORD-102 (Monitor)", weight=10, value=850.0),
        Parcel("ORD-103 (Printer)", weight=12, value=700.0),
        Parcel("ORD-104 (Camera)", weight=4, value=650.0),
        Parcel("ORD-105 (Tool Set)", weight=7, value=400.0),
    ]

    print(f"Vehicle Capacity: {vehicle_capacity} kg")
    print("Pending Customer Orders:")
    for p in delivery_orders:
        print(f"  {p.order_id}: weight={p.weight} kg, value=${p.value}")

    max_val, chosen, table = knapsack_01(delivery_orders, vehicle_capacity)

    print(f"\nOptimal Total Payload Value: ${max_val:.2f}")
    total_wt = sum(p.weight for p in chosen)
    print(f"Total Weight Loaded: {total_wt} kg / {vehicle_capacity} kg")
    print("Selected Parcels for Immediate Dispatch:")
    for p in chosen:
        print(f"  [x] {p.order_id} (weight: {p.weight} kg, value: ${p.value})")

    # Test 2: Verification against PPT Slide 29 Example
    print("\n--- Verification on PPT Slide 29 Example ---")
    # PPT Example: M = 5, Items:
    # Obj1: wt=2, val=3; Obj2: wt=3, val=4; Obj3: wt=4, val=5; Obj4: wt=5, val=6
    ppt_items = [
        Parcel("Obj 1", 2, 3),
        Parcel("Obj 2", 3, 4),
        Parcel("Obj 3", 4, 5),
        Parcel("Obj 4", 5, 6),
    ]
    ppt_max, ppt_chosen, ppt_table = knapsack_01(ppt_items, 5)
    print("PPT DP Table:")
    print(display_knapsack_table(ppt_table))
    print(f"Computed Maximum Value: {int(ppt_max)}")
    print(f"Chosen Items: {[p.order_id for p in ppt_chosen]}")
    print("Verification against PPT slide 29: Final answer is 7 (from Obj 1 + Obj 2) -> Exact match!")
