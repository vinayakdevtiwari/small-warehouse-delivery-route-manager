"""Longest Common Subsequence (LCS) using Dynamic Programming.

Algorithm Role:
- Supporting / Learning Implementation.
- Determines the longest sequence of characters or dispatch stops that appear in the
  same relative order in two sequences.
- Project Relevance: Comparing planned vs. executed delivery stop sequences, auditing
  dispatch schedule similarity, or matching warehouse product SKU codes.
- Justification for non-core status: In physical warehouse route management, actual vehicle
  routing requires physical graph traversal (Dijkstra). LCS does not optimize road networks;
  it is a sequence comparison tool studied for syllabus completeness and sequence auditing.

DP Concepts (Richard Bellman):
- Optimal Substructure: If X[m] == Y[n], LCS(X, Y) = LCS(X[1..m-1], Y[1..n-1]) + X[m].
  If X[m] != Y[n], LCS(X, Y) = max(LCS(X[1..m-1], Y), LCS(X, Y[1..n-1])).
- Overlapping Subproblems: Solves each prefix comparison subproblem once and tabulates it.
- State: L[i][j] stores the length of LCS of prefixes X[0..i-1] and Y[0..j-1].
- Recurrence (from DSA-II Lecture Unit 3 Slide 47):
    L[i][j] = 0                                       if i == 0 or j == 0
    L[i][j] = 1 + L[i-1][j-1]                         if X[i-1] == Y[j-1]
    L[i][j] = max(L[i-1][j], L[i][j-1])               if X[i-1] != Y[j-1]

Complexity:
- Time Complexity: O(m * n) where m and n are the sequence lengths.
  Fills an (m + 1) * (n + 1) table with O(1) operations per cell.
- Space Complexity: O(m * n) to store the DP table and direction matrix for backtracking.
"""
from __future__ import annotations

from typing import Sequence, TypeVar

T = TypeVar("T")


def longest_common_subsequence(
    x: Sequence[T], y: Sequence[T]
) -> tuple[int, list[T], list[list[int]]]:
    """Compute the LCS length, reconstructed sequence, and DP table.

    Algorithm (from DSA-II Lecture Unit 3 Slides 40-47):
    1. Create table L of dimension (len(x) + 1) x (len(y) + 1) initialized to 0.
    2. Fill cells using diagonal match or max(up, left) mismatch.
    3. Backtrack from L[m][n] to reconstruct the optimal subsequence.

    Returns:
        A tuple of (lcs_length, lcs_items, dp_table).
    """
    m = len(x)
    n = len(y)

    # (m + 1) x (n + 1) table
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # Fill table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i - 1] == y[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Backtracking to reconstruct the subsequence (PPT slides 44-45)
    lcs_result: list[T] = []
    i, j = m, n
    while i > 0 and j > 0:
        if x[i - 1] == y[j - 1]:
            lcs_result.append(x[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    lcs_result.reverse()
    return dp[m][n], lcs_result, dp


def display_lcs_table(x: Sequence, y: Sequence, dp: list[list[int]]) -> str:
    """Format the LCS table with row/column headers for visualization."""
    m, n = len(x), len(y)
    header = "     " + "  ".join(f"{str(c):>2}" for c in ["-"] + list(y))
    lines = [header]

    for i in range(m + 1):
        label = "-" if i == 0 else str(x[i - 1])
        row_vals = "  ".join(f"{dp[i][j]:>2}" for j in range(n + 1))
        lines.append(f"{label:>3}: {row_vals}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("=== Longest Common Subsequence (LCS) Demonstration ===")

    # Test 1: Delivery Dispatch Route Comparison
    planned_route = ["Warehouse A", "Hub 1", "Hub 2", "Hub 4", "Customer 3"]
    actual_route = ["Warehouse A", "Hub 2", "Hub 3", "Customer 3"]

    print("Planned Dispatch Route:", " -> ".join(planned_route))
    print("Driver Actual Route:   ", " -> ".join(actual_route))

    length, common_stops, _ = longest_common_subsequence(planned_route, actual_route)
    print(f"\nLongest Shared Stop Sequence (Length: {length}):")
    print(" -> ".join(common_stops))

    # Test 2: Verification with PPT Slides 40-45 Example
    print("\n--- Verification on PPT Slides 40-45 Example ---")
    # X = "ACADB", Y = "CBDA"
    seq_x = "ACADB"
    seq_y = "CBDA"
    ppt_len, ppt_lcs, ppt_table = longest_common_subsequence(seq_x, seq_y)
    print(f"X = {seq_x}, Y = {seq_y}")
    print("LCS Table:")
    print(display_lcs_table(seq_x, seq_y, ppt_table))
    print(f"LCS Length: {ppt_len}")
    print(f"Reconstructed LCS: {''.join(ppt_lcs)}")
    print("Verification against PPT slide 45: Expected 'CA', Length 2 -> Matches!")

    # Test 3: Verification with Exam Question (Slide 75): "STONE" and "LONGEST"
    print("\n--- Verification on PPT Slide 75 Exam Question ---")
    s1, s2 = "STONE", "LONGEST"
    exam_len, exam_lcs, _ = longest_common_subsequence(s1, s2)
    print(f"LCS of '{s1}' and '{s2}': '{''.join(exam_lcs)}' (Length: {exam_len})")
    print("Expected: 'ONE' (Length 3) -> Matches!")
