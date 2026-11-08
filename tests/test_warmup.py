"""Public tests for Task 0 - Warm-up (not graded)."""

from core.warmup import cheapest_neighbour, count_terrain
from world.desert_map import DesertMap

#   B r d        the base B stands on sand
#   . # d
TINY = DesertMap.from_strings([
    "Brd",
    ".#d",
])


def test_count_terrain_tiny():
    got = count_terrain(TINY)
    want = {".": 2, "r": 1, "d": 2, "#": 1}
    assert got == want, f"expected {want}, got {got}"


def test_count_terrain_generated_map():
    world = DesertMap.generate(seed=11)
    got = count_terrain(world)
    assert sum(got.values()) == world.rows * world.cols, \
        f"the counts must add up to rows*cols = {world.rows * world.cols}, got {sum(got.values())}"


def test_cheapest_neighbour():
    # neighbours of (0, 1) in order up, right, down, left: (0, 2) dunes, (0, 0) sand
    assert cheapest_neighbour(TINY, (0, 1)) == (0, 0), "sand (cost 1) beats dunes (cost 3)"
    # neighbours of (1, 2): up (0, 2) dunes; (1, 1) is a mountain, so only one choice
    assert cheapest_neighbour(TINY, (1, 2)) == (0, 2)


def test_cheapest_neighbour_ties_and_none():
    flat = DesertMap.from_strings(["...", ".B.", "..."])
    assert cheapest_neighbour(flat, (1, 1)) == (0, 1), "on a tie keep the first neighbour (up)"
    walled = DesertMap.from_strings(["#.#", "#B#", "###"])
    assert cheapest_neighbour(walled, (1, 1)) == (0, 1)
    alone = DesertMap.from_strings(["###", "#B#", "###"])
    assert cheapest_neighbour(alone, (1, 1)) is None, "no passable neighbour -> None"
