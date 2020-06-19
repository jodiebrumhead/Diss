import numpy as np

"""Minimum Cost Path"""

# https://www.geeksforgeeks.org/min-cost-path-dp-6/

# Dynamic Programming Python implementation of Min Cost Path
# problem
R = 4
C = 4


def minCost(cost, m, n):
    # Instead of following line, we can use int tc[m+1][n+1] or
    # dynamically allocate memoery to save space. The following
    # line is used to keep te program simple and make it working
    # on all compilers.
    tc = [[0 for x in range(C)] for x in range(R)]

    tc[0][0] = cost[0][0]


    # Initialize first column of total cost(tc) array
    for i in range(1, m + 1):
        tc[i][0] = tc[i - 1][0] + cost[i][0]

    # Initialize first row of tc array
    for j in range(1, n + 1):
        tc[0][j] = tc[0][j - 1] + cost[0][j]

    # Construct rest of the tc array
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            tc[i][j] = min(tc[i - 1][j - 1], tc[i - 1][j], tc[i][j - 1]) + cost[i][j]

    print(tc)
    return tc[m][n]


# Driver program to test above functions
cost = np.array([[1, 2, 3, 9],
                [4, 8, 2, 1],
                [1, 5, 3, 4],
                [2, 7, 3, 5]])

cost = np.flip(cost, (0))

print(cost)

print(minCost(cost, 3, 0))

# For each service calculate a full layer?
# Then find where points lie

# Need to cover full area...
