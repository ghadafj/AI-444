"""Public tests for Phase 1 - Search."""

from core.search import GridProblem, astar, bfs, euclidean, manhattan, path_cost, ucs
from world.desert_map import DesertMap

#   B d d d .        top route: 4 moves but crosses 3 dunes  -> cost 10
#   . # d # .        bottom route: 8 moves on sand           -> cost 8
#   . . . . .
SMALL = DesertMap.from_strings([
    "Bddd.",
    ".#d#.",
    ".....",
])
START, GOAL = (0, 0), (0, 4)


def _valid(problem, result):
    path = result.path
    assert path, "no path returned"
    assert path[0] == problem.start, f"path must start at {problem.start}, got {path[0]}"
    assert path[-1] == problem.goal, f"path must end at {problem.goal}, got {path[-1]}"
    for a, b in zip(path, path[1:]):
        assert b in problem.neighbors(a), f"illegal move {a} -> {b}"
    assert abs(result.cost - path_cost(problem, path)) < 1e-9, \
        f"cost {result.cost} does not match the path cost {path_cost(problem, path)}"
    assert result.expanded > 0, "expanded must count the cells taken out of the frontier"


def test_heuristics():
    assert manhattan((0, 0), (2, 3)) == 5, "manhattan((0,0),(2,3)) should be 5"
    assert abs(euclidean((0, 0), (3, 4)) - 5.0) < 1e-9, "euclidean((0,0),(3,4)) should be 5.0"


def test_bfs_fewest_moves():
    p = GridProblem(SMALL, START, GOAL)
    r = bfs(p)
    _valid(p, r)
    assert len(r.path) == 5, f"BFS should use 4 moves (5 cells), got {len(r.path)} cells"
    assert r.cost == 10, f"the BFS route crosses 3 dunes: cost 10, got {r.cost}"


def test_ucs_cheapest():
    p = GridProblem(SMALL, START, GOAL)
    r = ucs(p)
    _valid(p, r)
    assert r.cost == 8, f"UCS should find cost 8 (around the dunes), got {r.cost}"


def test_astar_cheapest():
    for h in (manhattan, euclidean):
        p = GridProblem(SMALL, START, GOAL)
        r = astar(p, h)
        _valid(p, r)
        assert r.cost == 8, f"A* with {h.__name__} should find cost 8, got {r.cost}"


def test_no_path():
    walled = DesertMap.from_strings(["B.#.", "..#.", "###."])
    p = GridProblem(walled, (0, 0), (0, 3))
    for algo in (bfs, ucs, astar):
        r = algo(p)
        assert r.path == [], f"{algo.__name__}: goal behind mountains must return an empty path"


def test_allowed_cells_only():
    allowed = {(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (1, 4), (0, 4)}
    p = GridProblem(SMALL, START, GOAL, allowed=allowed)
    for algo in (bfs, ucs, astar):
        r = algo(p)
        _valid(p, r)
        assert set(r.path) <= allowed, f"{algo.__name__} left the allowed cells"


def test_astar_beats_ucs_on_generated_map():
    world = DesertMap.generate(444)
    p = GridProblem(world, world.base, world.last_signal)
    ru, ra, rb = ucs(p), astar(p, manhattan), bfs(p)
    _valid(p, ru)
    _valid(p, ra)
    _valid(p, rb)
    assert ra.cost == ru.cost, f"A* cost {ra.cost} must equal UCS cost {ru.cost}"
    assert ra.expanded <= ru.expanded, \
        f"A* expanded {ra.expanded} cells, UCS {ru.expanded}: A* should expand fewer"
    assert len(rb.path) <= len(ru.path), "BFS must use the fewest moves"
    assert rb.cost >= ru.cost, "no path can be cheaper than the UCS path"
