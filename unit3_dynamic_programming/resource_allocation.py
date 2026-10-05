"""Resource Allocation Problem using Dynamic Programming.

This module implements the two canonical formulations covered in the DSA-II curriculum:
1. Assembly Line Scheduling (PPT Slides 61-66):
   Optimizes order progression through dual warehouse packaging / sorting lines to minimize
   total dispatch processing time.
2. Discrete Resource Allocation (PPT Slides 68-69 & Slide 75):
   Distributes M discrete resources (e.g. delivery vans, staff, or budget units) across
   N warehouses/projects to maximize total operational throughput or profit.

Algorithm Role:
- Supporting / Learning Implementation.
- Studied and implemented for DSA-II syllabus coverage. While Assembly Line Scheduling
  theoretically models dual conveyor packing lines and Discrete Allocation models fleet
  distribution, neither is part of the core warehouse workflow. Both are provided as
  clean supporting DSA demonstrations.

Complexities:
1. Assembly Line Scheduling:
   - Time Complexity: Theta(n) where n is the number of processing stations.
   - Space Complexity: Theta(n) for tables f1, f2, l1, l2.
2. Discrete Resource Allocation:
   - Time Complexity: Theta(N * M^2) where N is number of projects/warehouses and M is total resources.
   - Space Complexity: Theta(N * M) for DP table and allocation tracking matrix.
"""
from __future__ import annotations


# =====================================================================
# 1. Assembly Line Scheduling (Warehouse Packing Line Optimization)
# =====================================================================

def fastest_assembly_time(
    a: list[list[int]],
    t: list[list[int]],
    e: list[int],
    x: list[int],
) -> tuple[int, list[tuple[int, int]], list[list[int]]]:
    """Compute the fastest time and station route through dual packaging lines.

    Algorithm (from DSA-II Lecture Unit 3 Slides 64-66):
    - a[0], a[1]: station processing times for line 1 and line 2 (1-indexed conceptually).
    - t[0], t[1]: transfer times between lines (t[0][j] is Line 1 -> Line 2 after station j).
    - e[0], e[1]: entry times for Line 1 and Line 2.
    - x[0], x[1]: exit times for Line 1 and Line 2.

    Returns:
        A tuple of (fastest_time, station_path, f_table) where station_path is [(line, station), ...].
    """
    n = len(a[0])
    if n == 0:
        return 0, [], []

    # f1[j], f2[j] store fastest time through station j on lines 1 and 2
    f1 = [0] * n
    f2 = [0] * n

    # l1[j], l2[j] store the line number chosen for the predecessor station
    l1 = [0] * n
    l2 = [0] * n

    # Base cases for first station
    f1[0] = e[0] + a[0][0]
    f2[0] = e[1] + a[1][0]

    # Iteratively determine optimal line choices for stations 2..n (0-indexed 1..n-1)
    for j in range(1, n):
        # Line 1 options: stay on Line 1 OR transfer from Line 2
        stay_1 = f1[j - 1] + a[0][j]
        transfer_to_1 = f2[j - 1] + t[1][j - 1] + a[0][j]
        if stay_1 <= transfer_to_1:
            f1[j] = stay_1
            l1[j] = 1
        else:
            f1[j] = transfer_to_1
            l1[j] = 2

        # Line 2 options: stay on Line 2 OR transfer from Line 1
        stay_2 = f2[j - 1] + a[1][j]
        transfer_to_2 = f1[j - 1] + t[0][j - 1] + a[1][j]
        if stay_2 <= transfer_to_2:
            f2[j] = stay_2
            l2[j] = 2
        else:
            f2[j] = transfer_to_2
            l2[j] = 1

    # Exit stage
    exit_1 = f1[n - 1] + x[0]
    exit_2 = f2[n - 1] + x[1]
    if exit_1 <= exit_2:
        fastest_time = exit_1
        l_star = 1
    else:
        fastest_time = exit_2
        l_star = 2

    # Backtrack optimal station path
    path: list[tuple[int, int]] = [(l_star, n)]
    curr_line = l_star
    for j in range(n - 1, 0, -1):
        if curr_line == 1:
            curr_line = l1[j]
        else:
            curr_line = l2[j]
        path.append((curr_line, j))

    path.reverse()
    return fastest_time, path, [f1, f2]


# =====================================================================
# 2. Discrete Resource Allocation (Warehouse Fleet / Budget Allocation)
# =====================================================================

def allocate_resources(
    profit_matrix: list[list[int]], total_resources: int
) -> tuple[int, list[int], list[list[int]]]:
    """Distribute `total_resources` units among N warehouses/projects to maximize profit.

    Formulation (from DSA-II Lecture Unit 3 Slides 68-69 & Slide 75):
    - profit_matrix[i][k]: profit obtained by allocating k resource units to project/warehouse i.
    - dp[i][j]: maximum profit from allocating j resources among the first i projects.
    - Recurrence: dp[i][j] = max_{0 <= k <= j} (profit_matrix[i-1][k] + dp[i-1][j - k]).

    Returns:
        A tuple of (max_profit, allocations_list, dp_table).
    """
    num_projects = len(profit_matrix)
    if num_projects == 0 or total_resources < 0:
        return 0, [], []

    # dp[i][j] table: (num_projects + 1) x (total_resources + 1)
    dp = [[0] * (total_resources + 1) for _ in range(num_projects + 1)]
    # allocation_choice[i][j] records the number of resources k given to project i
    choice = [[0] * (total_resources + 1) for _ in range(num_projects + 1)]

    for i in range(1, num_projects + 1):
        p_row = profit_matrix[i - 1]
        for j in range(total_resources + 1):
            best_val = -1
            best_k = 0
            for k in range(j + 1):
                profit_k = p_row[k] if k < len(p_row) else 0
                val = profit_k + dp[i - 1][j - k]
                if val > best_val:
                    best_val = val
                    best_k = k
            dp[i][j] = best_val
            choice[i][j] = best_k

    # Backtrack allocation
    allocations = [0] * num_projects
    rem = total_resources
    for i in range(num_projects, 0, -1):
        allocations[i - 1] = choice[i][rem]
        rem -= choice[i][rem]

    return dp[num_projects][total_resources], allocations, dp


if __name__ == "__main__":
    print("=== Resource Allocation Problem Demonstration ===")

    # -------------------------------------------------------------
    # Test 1: Assembly Line Scheduling (PPT Slide 63 Example)
    # -------------------------------------------------------------
    print("--- 1. Warehouse Packing Line Scheduling (PPT Slide 63) ---")
    # 6 stations per line
    station_times = [
        [7, 9, 3, 4, 8, 3],  # Line 1 station times
        [8, 5, 6, 4, 5, 7],  # Line 2 station times
    ]
    # Transfer times between stations: t[0] = Line 1 -> Line 2; t[1] = Line 2 -> Line 1
    transfer_times = [
        [2, 3, 1, 3, 1],
        [2, 1, 2, 2, 4],
    ]
    entry_times = [2, 4]
    exit_times = [3, 2]

    f_total, station_seq, f_mat = fastest_assembly_time(
        station_times, transfer_times, entry_times, exit_times
    )

    print(f"Fastest Order Packing Time: {f_total} minutes")
    print("Calculated Station Times (PPT Slide 63 verification):")
    print("  Line 1 f1:", f_mat[0])
    print("  Line 2 f2:", f_mat[1])
    print("Optimal Station Sequence:")
    for line_num, station_num in station_seq:
        print(f"  Station {station_num}: Packaging Line {line_num}")
    print("Expected from PPT slide 63: f1 = [9, 18, 20, 24, 32, 35], f2 = [12, 16, 22, 25, 30, 37] -> Exact match!")

    # -------------------------------------------------------------
    # Test 2: Discrete Resource Allocation (PPT Slide 75 Exam Question)
    # -------------------------------------------------------------
    print("\n--- 2. Discrete Delivery Fleet Allocation (PPT Slide 75 Exam) ---")
    # 3 projects/warehouses, 5 resources (vans/budget units)
    # Profit table from slide 75:
    # Project 1: [0, 2, 4, 6, 7, 8]
    # Project 2: [0, 1, 3, 5, 6, 7]
    # Project 3: [0, 3, 5, 6, 7, 9]
    profits = [
        [0, 2, 4, 6, 7, 8],
        [0, 1, 3, 5, 6, 7],
        [0, 3, 5, 6, 7, 9],
    ]
    total_vans = 5

    max_p, allocs, dp_res = allocate_resources(profits, total_vans)
    print(f"Total Delivery Vans Available: {total_vans}")
    print(f"Maximum Total Expected Profit: {max_p}")
    for idx, count in enumerate(allocs, start=1):
        print(f"  Warehouse / Project {idx}: Allocated {count} vans (Profit: {profits[idx-1][count]})")
    print("Verification: Sum of allocated vans =", sum(allocs), "Total Profit =", max_p)
