"""
PHASE 3 - Planning (20 points)
SE 444 Course Project: Desert Rescue Drone

The hiker is found. Now the drone must deliver two items and come home:
    - the medical KIT, kept at the Base
    - a WATER bottle, kept at the Oasis
The drone carries one item at a time and has a small fuel tank.

We describe the world with STRIPS, exactly as in Lecture 9:
    a STATE is a frozenset of true facts (closed-world: anything missing is false)
    an ACTION has a precondition, an add list and a delete list

Facts used (all strings):
    At(Base)  At(Oasis)  At(Hiker)          where the drone is
    Fuel(0) ... Fuel(4)                      fuel units left (exactly one is true)
    ItemAt(Kit,Base)  ItemAt(Water,Oasis)    where an item waits
    Holding(Kit)  Holding(Water)  HandEmpty  what the drone carries
    Delivered(Kit)  Delivered(Water)         the hiker has the item

Action schemas:
    Fly(a, b, k)   PROVIDED     pre: At(a), Fuel(k)          add: At(b), Fuel(k-c)   del: At(a), Fuel(k)
                                (c = fuel needed for a->b, computed from YOUR map with A*)
    Refuel(s, k)   PROVIDED     pre: At(s), Fuel(k)          add: Fuel(MAX)          del: Fuel(k)
                                (only at Base and Oasis)
    PickUp(i, s)   YOU WRITE    pre: At(s), ItemAt(i,s), HandEmpty
                                add: Holding(i)              del: ItemAt(i,s), HandEmpty
    Drop(i)        YOU WRITE    pre: At(Hiker), Holding(i)
                                add: Delivered(i), HandEmpty del: Holding(i)

Goal: Delivered(Kit), Delivered(Water), At(Base)

You implement:
    Action.is_applicable(state)
    Action.apply(state)
    ground_pickup_and_drop(items)
    forward_bfs(problem)           shortest plan (fewest actions)
    goal_count(state, goal)        heuristic: goal facts not yet true
    forward_astar(problem, h)      A* over states, every action costs 1

Test:  python main.py --test planning
Demo:  python main.py --id YOUR_ID --phase planning
"""

from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, FrozenSet, List, Optional, Tuple

State = FrozenSet[str]

MAX_FUEL = 4
SITES = ("Base", "Oasis", "Hiker")
REFUEL_SITES = ("Base", "Oasis")


# ---------------------------------------------------------------- ACTIONS
@dataclass(frozen=True)
class Action:
    name: str
    pre: FrozenSet[str]
    add: FrozenSet[str]
    delete: FrozenSet[str]

    def is_applicable(self, state: State) -> bool:
        """True if every precondition fact is in `state`."""
        # YOUR CODE HERE
        raise NotImplementedError("Action.is_applicable() not implemented yet")

    def apply(self, state: State) -> State:
        """Result of doing the action: (state - delete) | add. Return a frozenset."""
        # YOUR CODE HERE
        raise NotImplementedError("Action.apply() not implemented yet")

    def __str__(self) -> str:
        return self.name


def make_action(name: str, pre, add, delete) -> Action:
    """Helper: make_action("PickUp(Kit,Base)", [...], [...], [...]). PROVIDED."""
    return Action(name, frozenset(pre), frozenset(add), frozenset(delete))


@dataclass
class PlanningProblem:
    initial: State
    goal: FrozenSet[str]
    actions: List[Action] = field(default_factory=list)

    def is_goal(self, state: State) -> bool:
        return self.goal <= state


@dataclass
class PlanResult:
    plan: Optional[List[Action]]
    expanded: int = 0

    @property
    def found(self) -> bool:
        return self.plan is not None


# ---------------------------------------------------------------- PROVIDED SCHEMAS
def ground_fly_and_refuel(fuel_cost: Dict[Tuple[str, str], int]) -> List[Action]:
    """All ground Fly and Refuel actions. PROVIDED.

    fuel_cost[(a, b)] = fuel units needed to fly from site a to site b.
    """
    actions = []
    for (a, b), c in sorted(fuel_cost.items()):
        for k in range(c, MAX_FUEL + 1):
            actions.append(make_action(
                f"Fly({a},{b},{k})",
                pre=[f"At({a})", f"Fuel({k})"],
                add=[f"At({b})", f"Fuel({k - c})"],
                delete=[f"At({a})", f"Fuel({k})"] if c > 0 else [f"At({a})"]))
    for s in REFUEL_SITES:
        for k in range(0, MAX_FUEL):
            actions.append(make_action(
                f"Refuel({s},{k})",
                pre=[f"At({s})", f"Fuel({k})"],
                add=[f"Fuel({MAX_FUEL})"],
                delete=[f"Fuel({k})"]))
    return actions


# ---------------------------------------------------------------- YOUR SCHEMAS
def ground_pickup_and_drop(items: Dict[str, str]) -> List[Action]:
    """Ground the PickUp and Drop schemas.

    items maps each item to the site where it waits, e.g. {"Kit": "Base", "Water": "Oasis"}.

    Return one PickUp(i,s) action per item (at its own site) and one Drop(i) per item.
    Use the exact names "PickUp(Kit,Base)" and "Drop(Kit)" and the facts listed at the
    top of this file.
    """
    # YOUR CODE HERE
    raise NotImplementedError("ground_pickup_and_drop() not implemented yet")


def build_rescue_problem(fuel_cost: Dict[Tuple[str, str], int],
                         items: Optional[Dict[str, str]] = None,
                         start_fuel: int = MAX_FUEL) -> PlanningProblem:
    """The delivery problem. PROVIDED."""
    items = items or {"Kit": "Base", "Water": "Oasis"}
    initial = {"At(Base)", f"Fuel({start_fuel})", "HandEmpty"}
    initial |= {f"ItemAt({i},{s})" for i, s in items.items()}
    goal = {f"Delivered({i})" for i in items} | {"At(Base)"}
    actions = ground_fly_and_refuel(fuel_cost) + ground_pickup_and_drop(items)
    return PlanningProblem(frozenset(initial), frozenset(goal), actions)


# ---------------------------------------------------------------- PLANNERS
def forward_bfs(problem: PlanningProblem) -> PlanResult:
    """Forward state-space search with BFS. Returns the plan with the FEWEST actions.

    Hints: the same as BFS in Phase 1, but a node is a STATE (frozenset) and the
    neighbours of a state are action.apply(state) for every applicable action.
    Keep parent[state] = (previous_state, action) to rebuild the plan.
    Count one expansion per state popped. Return PlanResult(None, expanded) if no plan.
    """
    # YOUR CODE HERE
    raise NotImplementedError("forward_bfs() not implemented yet")


def goal_count(state: State, goal: FrozenSet[str]) -> int:
    """Heuristic: how many goal facts are not yet true in `state`."""
    # YOUR CODE HERE
    raise NotImplementedError("goal_count() not implemented yet")


def forward_astar(problem: PlanningProblem,
                  h: Callable[[State, FrozenSet[str]], int] = goal_count) -> PlanResult:
    """A* over states. Every action costs 1, so g = number of actions so far.
    f = g + h(state, problem.goal). Test for the goal when you pop."""
    # YOUR CODE HERE
    raise NotImplementedError("forward_astar() not implemented yet")


# ---------------------------------------------------------------- PROVIDED
def check_plan(problem: PlanningProblem, plan: List[Action]) -> Tuple[bool, str]:
    """Execute a plan step by step and say whether it reaches the goal. PROVIDED."""
    state = problem.initial
    for i, action in enumerate(plan, 1):
        if not action.is_applicable(state):
            missing = sorted(action.pre - state)
            return False, f"step {i} {action.name}: precondition missing {missing}"
        state = action.apply(state)
    if not problem.is_goal(state):
        return False, f"goal not reached, missing {sorted(problem.goal - state)}"
    return True, "plan reaches the goal"
