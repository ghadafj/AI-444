"""Public tests for Phase 3 - Planning."""

from core.planning import (build_rescue_problem, check_plan, forward_astar, forward_bfs,
                           goal_count, ground_pickup_and_drop, make_action)

ALL_ONE = {(a, b): 1 for a in ("Base", "Oasis", "Hiker")
           for b in ("Base", "Oasis", "Hiker") if a != b}
ALL_TWO = {k: 2 for k in ALL_ONE}


def test_applicable_and_apply():
    act = make_action("PickUp(Kit,Base)",
                      pre=["At(Base)", "ItemAt(Kit,Base)", "HandEmpty"],
                      add=["Holding(Kit)"],
                      delete=["ItemAt(Kit,Base)", "HandEmpty"])
    s = frozenset({"At(Base)", "ItemAt(Kit,Base)", "HandEmpty", "Fuel(4)"})
    assert act.is_applicable(s), "all preconditions hold"
    assert not act.is_applicable(frozenset({"At(Base)"})), "preconditions missing"
    nxt = act.apply(s)
    assert isinstance(nxt, frozenset), "apply() must return a frozenset"
    assert nxt == frozenset({"At(Base)", "Holding(Kit)", "Fuel(4)"}), f"wrong result {sorted(nxt)}"
    assert "HandEmpty" in s, "apply() must not change the input state"


def test_ground_pickup_and_drop():
    acts = {a.name: a for a in ground_pickup_and_drop({"Kit": "Base", "Water": "Oasis"})}
    assert set(acts) == {"PickUp(Kit,Base)", "Drop(Kit)", "PickUp(Water,Oasis)", "Drop(Water)"}, \
        f"wrong action names {sorted(acts)}"
    pick = acts["PickUp(Water,Oasis)"]
    assert pick.pre == frozenset({"At(Oasis)", "ItemAt(Water,Oasis)", "HandEmpty"}), "PickUp pre"
    assert pick.add == frozenset({"Holding(Water)"}), "PickUp add"
    assert pick.delete == frozenset({"ItemAt(Water,Oasis)", "HandEmpty"}), "PickUp delete"
    drop = acts["Drop(Kit)"]
    assert drop.pre == frozenset({"At(Hiker)", "Holding(Kit)"}), "Drop pre"
    assert drop.add == frozenset({"Delivered(Kit)", "HandEmpty"}), "Drop add"
    assert drop.delete == frozenset({"Holding(Kit)"}), "Drop delete"


def test_goal_count():
    goal = frozenset({"A", "B", "C"})
    assert goal_count(frozenset({"A", "X"}), goal) == 2
    assert goal_count(goal, goal) == 0


def test_bfs_short_flights():
    prob = build_rescue_problem(ALL_ONE)
    res = forward_bfs(prob)
    assert res.found, "a plan exists"
    ok, msg = check_plan(prob, res.plan)
    assert ok, msg
    assert len(res.plan) == 8, f"the shortest plan has 8 actions, got {len(res.plan)}"


def test_bfs_needs_refuel():
    prob = build_rescue_problem(ALL_TWO)
    res = forward_bfs(prob)
    assert res.found, "a plan exists"
    ok, msg = check_plan(prob, res.plan)
    assert ok, msg
    assert len(res.plan) == 9, f"with 2-unit flights the shortest plan has 9 actions, got {len(res.plan)}"
    assert any(a.name.startswith("Refuel") for a in res.plan), "this plan must refuel once"


def test_astar_matches_bfs():
    for costs in (ALL_ONE, ALL_TWO):
        prob = build_rescue_problem(costs)
        b, a = forward_bfs(prob), forward_astar(prob)
        assert a.found, "A* must find a plan"
        ok, msg = check_plan(prob, a.plan)
        assert ok, msg
        assert len(a.plan) == len(b.plan), "goal-count is admissible here, so A* must be optimal"
        assert a.expanded <= b.expanded, f"A* expanded {a.expanded} states, BFS {b.expanded}"
