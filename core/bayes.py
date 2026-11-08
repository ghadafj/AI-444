"""
PHASE 4 - Probability (20 points)
SE 444 Course Project: Desert Rescue Drone

Where is the hiker? The drone keeps a BELIEF MAP: for every passable cell c,
    belief[c] = P(hiker is in c | everything observed so far)
All values are >= 0 and sum to 1.

The thermal camera scans the cell under the drone:
    P(see hiker | hiker in c)     = d(c)   (sand 0.9, rocks 0.7, dunes 0.5)
    P(see hiker | hiker not in c) = 0      (no false alarms)

When the camera sees NOTHING in cell c, Bayes' rule gives the new belief:

    P(miss)            = 1 - belief[c] * d(c)
    new belief[c]      = belief[c] * (1 - d(c)) / P(miss)
    new belief[x != c] = belief[x] / P(miss)

(Derive this in your report: hypothesis H_x = "hiker in x", evidence = "miss in c".)

You implement:
    normalize(weights)                          -> belief that sums to 1
    update_after_miss(belief, cell, d)          -> new belief (do NOT change the input)
    detection_chance(belief, cell, d)           -> P(find the hiker on the next scan of cell)
    choose_search_cell(belief, d_of, candidates, travel_cost) -> best cell to scan next

Test:  python main.py --test bayes
Demo:  python main.py --id YOUR_ID --phase bayes
"""

from __future__ import annotations

from typing import Callable, Dict, Iterable, List, Optional, Tuple

from world.desert_map import Cell

Belief = Dict[Cell, float]


def normalize(weights: Dict[Cell, float]) -> Belief:
    """Divide every weight by the total so the values sum to 1.
    Raise ValueError if the total is 0."""
    # YOUR CODE HERE
    raise NotImplementedError("normalize() not implemented yet")


def update_after_miss(belief: Belief, cell: Cell, p_detect: float) -> Belief:
    """New belief after scanning `cell` and seeing nothing (formula above).
    Return a NEW dict; the input dict must not change."""
    # YOUR CODE HERE
    raise NotImplementedError("update_after_miss() not implemented yet")


def detection_chance(belief: Belief, cell: Cell, p_detect: float) -> float:
    """P(the next scan of `cell` finds the hiker) = belief[cell] * d(cell)."""
    # YOUR CODE HERE
    raise NotImplementedError("detection_chance() not implemented yet")


def choose_search_cell(belief: Belief,
                       p_detect_of: Callable[[Cell], float],
                       candidates: Iterable[Cell],
                       travel_cost: Callable[[Cell], float]) -> Optional[Cell]:
    """Pick the candidate cell with the highest score

        score(c) = detection_chance(belief, c, d(c)) / (1 + travel_cost(c))

    i.e. "chance of finding the hiker per unit of fuel". Break ties by the smaller
    cell tuple, so results are reproducible. Return None if there are no candidates.
    """
    # YOUR CODE HERE
    raise NotImplementedError("choose_search_cell() not implemented yet")


# ---------------------------------------------------------------- PROVIDED
def most_likely(belief: Belief, k: int = 5) -> List[Tuple[Cell, float]]:
    """The k cells with the highest belief. PROVIDED."""
    return sorted(belief.items(), key=lambda kv: (-kv[1], kv[0]))[:k]


def entropy_bits(belief: Belief) -> float:
    """How uncertain the belief is, in bits (lower = more certain). PROVIDED."""
    import math
    return -sum(p * math.log2(p) for p in belief.values() if p > 0)
