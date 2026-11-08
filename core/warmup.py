"""
TASK 0 - Warm-up (0 points, NOT graded)
SE 444 Course Project: Desert Rescue Drone

Do this first. It teaches you the workflow (read the docstring, run the test,
write a little code, run the test again) on two small functions, before the real phases.

You implement:
    count_terrain(world)              how many cells of each terrain the map has
    cheapest_neighbour(world, cell)   the neighbour that is cheapest to fly into

Useful DesertMap methods (see world/desert_map.py):
    world.rows, world.cols      size of the grid
    world.terrain(cell)         one letter: "." sand, "r" rocks, "d" dunes, "#" mountain
    world.neighbors(cell)       passable cells up, right, down, left of cell
    world.cost(cell)            cost to ENTER a cell: sand 1, rocks 2, dunes 3

Test:  python main.py --test warmup
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

from world.desert_map import DesertMap

Cell = Tuple[int, int]


def count_terrain(world: DesertMap) -> Dict[str, int]:
    """Count the cells of each terrain letter on the whole map.

    Example: a map with rows ".r" and "d#" gives {".": 1, "r": 1, "d": 1, "#": 1}
    Hints:
      - loop over every row r in range(world.rows) and column c in range(world.cols)
      - the letter of a cell is world.terrain((r, c))
      - add 1 to that letter's count in a dict
    """
    # YOUR CODE HERE
    raise NotImplementedError("count_terrain() not implemented yet")


def cheapest_neighbour(world: DesertMap, cell: Cell) -> Optional[Cell]:
    """Return the passable neighbour of `cell` with the smallest world.cost().

    Ties: keep the FIRST one in the order world.neighbors() gives (up, right, down, left).
    If `cell` has no passable neighbour, return None.
    Hints:
      - start with best = None
      - for each n in world.neighbors(cell): keep n if best is None
        or world.cost(n) < world.cost(best)   (strictly smaller keeps the first on ties)
    """
    # YOUR CODE HERE
    raise NotImplementedError("cheapest_neighbour() not implemented yet")
