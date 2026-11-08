"""
PHASE 1 - Search (25 points)
SE 444 Course Project: Desert Rescue Drone

The drone must fly from one cell to another. Each cell it enters costs fuel:
sand 1, rocks 2, dunes 3. Mountains cannot be crossed.

You implement:
    bfs(problem)                  fewest moves, ignores cost
    ucs(problem)                  cheapest path
    astar(problem, heuristic)     cheapest path, explores fewer cells
    manhattan(a, b)               heuristic
    euclidean(a, b)               heuristic

Every function returns a SearchResult:
    path      list of cells from start to goal, both included ([] if no path)
    cost      sum of costs of the cells entered after the start
    expanded  how many cells you took out of the frontier (to compare algorithms)

Rules:
    - Use problem.neighbors(cell) and problem.cost(cell). Do not read the map directly,
      because the mission (Phase 5) restricts the drone to cells it knows are safe.
    - Count a cell as "expanded" when you take it OUT of the frontier.
    - Never expand the same cell twice.

Test:  python main.py --test search
Demo:  python main.py --id YOUR_ID --phase search
"""

from __future__ import annotations

import heapq
import math
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set

from world.desert_map import Cell, DesertMap


# ---------------------------------------------------------------- PROVIDED
@dataclass
class SearchResult:
    path: List[Cell] = field(default_factory=list)
    cost: float = 0.0
    expanded: int = 0

    @property
    def found(self) -> bool:
        return len(self.path) > 0


class GridProblem:
    """A route-finding problem on the desert map. PROVIDED.

    allowed: if given, the drone may only fly through these cells
             (the goal must be inside `allowed` too).
    """

    def __init__(self, world: DesertMap, start: Cell, goal: Cell,
                 allowed: Optional[Set[Cell]] = None):
        self.world = world
        self.start = start
        self.goal = goal
        self.allowed = allowed

    def is_goal(self, cell: Cell) -> bool:
        return cell == self.goal

    def neighbors(self, cell: Cell) -> List[Cell]:
        nbrs = self.world.neighbors(cell)
        if self.allowed is not None:
            nbrs = [n for n in nbrs if n in self.allowed]
        return nbrs

    def cost(self, cell: Cell) -> float:
        """Cost to ENTER `cell`."""
        return self.world.cost(cell)


def reconstruct_path(parent: Dict[Cell, Optional[Cell]], goal: Cell) -> List[Cell]:
    """Follow parent links back from goal to start. PROVIDED.
    `parent[start]` must be None."""
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    path.reverse()
    return path


def path_cost(problem: GridProblem, path: List[Cell]) -> float:
    """Cost of a path: sum of the costs of every cell after the first. PROVIDED."""
    return sum(problem.cost(c) for c in path[1:])


# ---------------------------------------------------------------- HEURISTICS
def manhattan(a: Cell, b: Cell) -> float:
    """Number of up/down/left/right moves between a and b, ignoring obstacles.

    Example: manhattan((0, 0), (2, 3)) == 5
    Why admissible here: every move enters a cell that costs at least 1.
    """
    # YOUR CODE HERE
    raise NotImplementedError("manhattan() not implemented yet")


def euclidean(a: Cell, b: Cell) -> float:
    """Straight-line distance between a and b.

    Example: euclidean((0, 0), (3, 4)) == 5.0
    """
    # YOUR CODE HERE
    raise NotImplementedError("euclidean() not implemented yet")


# ---------------------------------------------------------------- ALGORITHMS
def bfs(problem: GridProblem) -> SearchResult:
    """Breadth-First Search: the path with the FEWEST MOVES (ignores cost).

    Hints:
      - frontier = deque([start]); parent = {start: None}
      - pop from the LEFT (first in, first out); that pop is one expansion
      - if the popped cell is the goal: rebuild the path and return
      - add each neighbour not yet in `parent` to the right of the frontier
      - result cost: use path_cost(problem, path)
    """
    # YOUR CODE HERE
    raise NotImplementedError("bfs() not implemented yet")


def ucs(problem: GridProblem) -> SearchResult:
    """Uniform-Cost Search: the CHEAPEST path.

    Hints:
      - frontier is a heap of (g, tie, cell); use a counter as `tie`
      - g[cell] = best known cost from start; parent[cell] = previous cell
      - pop the cheapest entry; skip it if the cell was already expanded
      - test for the goal when you POP (not when you push) - this is what makes UCS optimal
      - for each neighbour n: new_g = g[cell] + problem.cost(n); keep it if it is better
    """
    # YOUR CODE HERE
    raise NotImplementedError("ucs() not implemented yet")


def astar(problem: GridProblem,
          heuristic: Callable[[Cell, Cell], float] = manhattan) -> SearchResult:
    """A* Search: like UCS but the heap is ordered by f = g + h(cell, goal).

    With an admissible heuristic (never overestimates), A* returns the same cost
    as UCS but usually expands fewer cells. Show this in your report.
    """
    # YOUR CODE HERE
    raise NotImplementedError("astar() not implemented yet")


