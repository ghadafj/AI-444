"""
PHASE 2 - Logic (20 points)
SE 444 Course Project: Desert Rescue Drone

The drone cannot see sandstorms. It only has a dust sensor:
    "dust here"     at least one neighbouring cell is a sandstorm
    "no dust here"  no neighbouring cell is a sandstorm

The drone keeps a Knowledge Base (KB) of propositional symbols and Horn rules,
and uses FORWARD CHAINING to prove which cells are safe and which are storms.

Symbols are strings built with sym():
    sym("Safe", (2, 3))    -> "Safe_2_3"     cell (2,3) has no sandstorm
    sym("Storm", (2, 3))   -> "Storm_2_3"    cell (2,3) is a sandstorm
    sym("Dust", (2, 3))    -> "Dust_2_3"     dust was sensed at (2,3)
    sym("NoDust", (2, 3))  -> "NoDust_2_3"   no dust was sensed at (2,3)

A Horn rule is (premises, conclusion):  all premises true  =>  conclusion true.
    Rule(frozenset({"NoDust_2_3"}), "Safe_2_4")

You implement:
    KnowledgeBase.tell_fact(symbol)
    KnowledgeBase.tell_rule(premises, conclusion)
    KnowledgeBase.forward_chain()        -> set of NEW symbols proved
    KnowledgeBase.ask(symbol)            -> True if the KB proves it
    percept_rules(cell, dust, neighbors) -> facts and rules for one dust reading

Test:  python main.py --test logic
Demo:  python main.py --id YOUR_ID --phase logic
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Set, Tuple

from world.desert_map import Cell, DesertMap


# ---------------------------------------------------------------- PROVIDED
def sym(kind: str, cell: Cell) -> str:
    """sym("Safe", (2, 3)) -> "Safe_2_3"."""
    return f"{kind}_{cell[0]}_{cell[1]}"


@dataclass(frozen=True)
class Rule:
    premises: FrozenSet[str]
    conclusion: str

    def __str__(self) -> str:
        return " ∧ ".join(sorted(self.premises)) + " ⇒ " + self.conclusion


# ---------------------------------------------------------------- YOUR KB
class KnowledgeBase:
    """A propositional KB of facts and Horn rules."""

    def __init__(self):
        self.facts: Set[str] = set()
        self.rules: List[Rule] = []

    def tell_fact(self, symbol: str) -> None:
        """Add a known-true symbol."""
        # YOUR CODE HERE
        raise NotImplementedError("tell_fact() not implemented yet")

    def tell_rule(self, premises: Iterable[str], conclusion: str) -> None:
        """Add the Horn rule  premises => conclusion.
        Do not store the same rule twice."""
        # YOUR CODE HERE
        raise NotImplementedError("tell_rule() not implemented yet")

    def forward_chain(self) -> Set[str]:
        """Apply rules until nothing new can be proved.

        Return the set of symbols that were NEW (not in self.facts before the call),
        and add them to self.facts.

        Simple method (full marks): loop over all rules; whenever every premise is in
        self.facts and the conclusion is not, add the conclusion. Repeat until a full
        pass adds nothing.

        Faster method (the agenda algorithm from the lecture): keep, for each rule, a
        count of premises not yet proved; pop symbols from an agenda and decrement.
        """
        # YOUR CODE HERE
        raise NotImplementedError("forward_chain() not implemented yet")

    def ask(self, symbol: str) -> bool:
        """True if the KB proves `symbol` (run forward chaining first)."""
        # YOUR CODE HERE
        raise NotImplementedError("ask() not implemented yet")


# ---------------------------------------------------------------- PERCEPTS
def percept_rules(cell: Cell, dust: bool,
                  neighbors: List[Cell]) -> Tuple[List[str], List[Rule]]:
    """Turn one dust reading into facts and Horn rules.

    The drone is at `cell` (so `cell` is safe: the drone survived there).
    `neighbors` are the passable neighbours of `cell`.

    Return (facts, rules):

      facts always contain  Safe_cell
      if no dust:  facts also contain NoDust_cell, and for every neighbour n a rule
                       NoDust_cell => Safe_n
      if dust:     facts also contain Dust_cell, and for every neighbour n a rule
                       Dust_cell ∧ Safe_m (for every OTHER neighbour m) => Storm_n
                   ("there is dust, all the others are safe, so it must be n")

    Example: cell (1,1), dust, neighbours [(0,1), (1,2)]
        facts = ["Safe_1_1", "Dust_1_1"]
        rules = [Rule({"Dust_1_1", "Safe_1_2"}, "Storm_0_1"),
                 Rule({"Dust_1_1", "Safe_0_1"}, "Storm_1_2")]
    """
    # YOUR CODE HERE
    raise NotImplementedError("percept_rules() not implemented yet")


# ---------------------------------------------------------------- PROVIDED
class SafetyMap:
    """What the drone has proved about sandstorms. PROVIDED - uses your KB.

    Call record_visit() every time the drone enters a cell.
    """

    def __init__(self, world: DesertMap):
        self.world = world
        self.kb = KnowledgeBase()
        self.visited: Set[Cell] = set()

    def record_visit(self, cell: Cell, dust: bool) -> Set[str]:
        self.visited.add(cell)
        facts, rules = percept_rules(cell, dust, self.world.neighbors(cell))
        for f in facts:
            self.kb.tell_fact(f)
        for r in rules:
            self.kb.tell_rule(r.premises, r.conclusion)
        return self.kb.forward_chain()

    def is_safe(self, cell: Cell) -> bool:
        return sym("Safe", cell) in self.kb.facts

    def is_storm(self, cell: Cell) -> bool:
        return sym("Storm", cell) in self.kb.facts

    def safe_cells(self) -> Set[Cell]:
        return {c for c in self.world.passable_cells() if self.is_safe(c)}

    def storm_cells(self) -> Set[Cell]:
        return {c for c in self.world.passable_cells() if self.is_storm(c)}
