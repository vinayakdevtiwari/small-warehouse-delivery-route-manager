"""Matrix Chain Multiplication (MCM) using Dynamic Programming.

Algorithm Role:
- Supporting / Learning Implementation.
- Finds the most computationally efficient parenthesization order for multiplying a chain
  of matrices to minimize the total number of scalar multiplications.
- Project Relevance: Optimizes multi-stage matrix transformation pipelines, such as cascading
  transition operators in multi-warehouse inventory forecasting or cost projection models.
- Justification for non-core status: Road deliveries physically follow geographical road links
  (handled by Dijkstra). Matrices are not chained during physical driving; MCM is studied for
  syllabus completeness and mastery of interval dynamic programming.

DP Concepts (Richard Bellman):
- Optimal Substructure: The optimal parenthesization of A[i..j] splits at some index k into
  two optimal sub-chains A[i..k] and A[k+1..j].
- Overlapping Subproblems: Multiple subchains overlap during evaluation, tabulated in m[i, j].
- State: m[i, j] is the minimum scalar multiplication cost to compute A[i..j].
- Recurrence (from DSA-II Lecture Unit 3 Slide 56):
    m[i, i] = 0
    m[i, j] = min_{i <= k < j} { m[i, k] + m[k+1, j] + p_{i-1} * p_k * p_j }
- Split tracker: s[i, j] records the optimal partition index k.

Complexity:
- Time Complexity: Theta(n^3) where n is the number of matrices.
  Three nested loops iterate over chain length (diff), start index (i), and split index (k).
- Space Complexity: Theta(n^2) for the cost table m and split table s.
"""
from __future__ import annotations


def matrix_chain_order(
    p: list[int],
) -> tuple[int, str, list[list[int]], list[list[int]]]:
    """Compute the minimum scalar multiplication cost and optimal parenthesization.

    Algorithm (from DSA-II Lecture Unit 3 Slides 56-57):
    1. n = len(p) - 1 matrices (A_1..A_n where A_i has dimension p[i-1] x p[i]).
    2. Initialize m[1..n, 1..n] to 0 on diagonal, infinity elsewhere.
    3. Loop chain length diff from 1 to n-1:
         Loop start index i from 1 to n - diff:
           j = i + diff
           Loop k from i to j-1:
             q = m[i, k] + m[k+1, j] + p[i-1] * p[k] * p[j]
             if q < m[i, j]:
               m[i, j] = q
               s[i, j] = k
    4. Construct optimal parenthesization using PRINT-OPTIMAL-OUTPUT(s, 1, n).

    Args:
        p: List of dimensions [p_0, p_1, ..., p_n].

    Returns:
        A tuple of (min_cost, parenthesization_string, m_table, s_table).
    """
    n = len(p) - 1
    if n < 1:
        return 0, "", [], []

    # 1-indexed tables of size (n + 1) x (n + 1)
    m = [[0] * (n + 1) for _ in range(n + 1)]
    s = [[0] * (n + 1) for _ in range(n + 1)]

    # diff is the subchain length - 1
    for diff in range(1, n):
        for i in range(1, n - diff + 1):
            j = i + diff
            m[i][j] = float("inf")  # type: ignore
            for k in range(i, j):
                q = m[i][k] + m[k + 1][j] + p[i - 1] * p[k] * p[j]
                if q < m[i][j]:
                    m[i][j] = q
                    s[i][j] = k

    def print_optimal_output(s_table: list[list[int]], i: int, j: int) -> str:
        """Recursive reconstruction of optimal parenthesization (PPT slide 57)."""
        if i == j:
            return f"A{i}"
        k = s_table[i][j]
        left = print_optimal_output(s_table, i, k)
        right = print_optimal_output(s_table, k + 1, j)
        return f"({left} x {right})"

    optimal_parens = print_optimal_output(s, 1, n)
    return int(m[1][n]), optimal_parens, m, s


def display_m_table(m: list[list[int]], n: int) -> str:
    """Format the upper-triangular cost table m into an aligned string."""
    width = 10
    header = "i \\ j".ljust(6) + "".join(f"A{j}".rjust(width) for j in range(1, n + 1))
    lines = [header, "-" * len(header)]
    for i in range(1, n + 1):
        row = [f"A{i}".ljust(6)]
        for j in range(1, n + 1):
            if j < i:
                row.append(".".rjust(width))
            else:
                row.append(str(m[i][j]).rjust(width))
        lines.append("".join(row))
    return "\n".join(lines)


if __name__ == "__main__":
    print("=== Matrix Chain Multiplication (MCM) Demonstration ===")

    # Test 1: Example from PPT Slides 52-55
    # A: 10x30, B: 30x5, C: 5x60, D: 60x8
    p1 = [10, 30, 5, 60, 8]
    print("Chain 1: 4 matrices with dimensions p = [10, 30, 5, 60, 8]")
    print("Matrices: A1(10x30), A2(30x5), A3(5x60), A4(60x8)")

    cost1, parens1, m1, s1 = matrix_chain_order(p1)
    print(f"\nMinimum Scalar Multiplications: {cost1}")
    print(f"Optimal Parenthesization: {parens1}")
    print("\nDP Cost Table m[i, j]:")
    print(display_m_table(m1, len(p1) - 1))

    # Test 2: University Exam Question from Slide 75:
    # A(5x4), B(4x6), C(6x2), D(2x7) -> p = [5, 4, 6, 2, 7]
    print("\n--- Verification on PPT Slide 75 Exam Question ---")
    p2 = [5, 4, 6, 2, 7]
    cost2, parens2, m2, s2 = matrix_chain_order(p2)
    print("Dimensions: p = [5, 4, 6, 2, 7]")
    print(f"Minimum Scalar Multiplications: {cost2}")
    print(f"Optimal Parenthesization: {parens2}")
    print("DP Cost Table:")
    print(display_m_table(m2, len(p2) - 1))
    print(f"Optimal split k at root s[1, 4] = {s2[1][4]}")
