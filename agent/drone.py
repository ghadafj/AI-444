"""
PHASE 5 - The full rescue mission (5 points + your demo video)
SE 444 Course Project: Desert Rescue Drone

This file joins your four phases into one agent:

    1. Bayes picks the most promising cell to scan          (Phase 4)
    2. Logic tells which cells are proved safe              (Phase 2)
    3. A* finds a route through safe cells only             (Phase 1)
    4. The drone flies, senses dust, scans with its camera,
       updates the KB and the belief map at every cell
    5. When the hiker is found, STRIPS plans the delivery   (Phase 3)

The search flies LOW (the camera needs it), so a sandstorm cell destroys the drone.
Delivery flights cruise HIGH above the storms, so Phase 3 ignores storms.

You implement only RescueDrone.plan_next_leg(). Everything else is PROVIDED.

Demo:  python main.py --id YOUR_ID --phase mission [--gui]
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Set, Tuple

from core.bayes import choose_search_cell, normalize, update_after_miss
from core.logic import SafetyMap
from core.planning import PlanResult, build_rescue_problem, forward_astar
from core.search import GridProblem, astar, manhattan
from world.desert_map import Cell, DesertMap

DEFAULT_BATTERY = 600
FUEL_UNIT_THRESHOLD = 15   # an A* route cost above this needs 2 fuel units, else 1


@dataclass
class Frame:
    """One snapshot of the mission, used by the viewer and the video."""
    pos: Cell
    battery: float
    event: str


@dataclass
class MissionReport:
    found: bool
    crashed: bool
    battery_left: float
    cells_flown: int
    scans: int
    safe_cells: int
    storms_proved: int
    hiker_belief_at_end: float
    delivery: Optional[PlanResult] = None
    reason: str = ""
    frames: List[Frame] = field(default_factory=list)


class RescueDrone:
    def __init__(self, world: DesertMap, battery: float = DEFAULT_BATTERY,
                 rng_seed: Optional[int] = None):
        self.world = world
        self.pos: Cell = world.base
        self.battery = battery
        self.safety = SafetyMap(world)
        self.belief = normalize(world.hiker_prior())
        seed = rng_seed if rng_seed is not None else (world.seed or 0) + 7
        self.rng = random.Random(seed)
        self.found = False
        self.crashed = False
        self.scans = 0
        self.cells_flown = 0
        self.trail: List[Cell] = [self.pos]
        self.excluded: Set[Cell] = set()
        self.frames: List[Frame] = []
        self._enter(self.pos)

    # ------------------------------------------------------------ PROVIDED
    def _log(self, event: str) -> None:
        self.frames.append(Frame(self.pos, self.battery, event))

    def _enter(self, cell: Cell) -> None:
        """Sense dust, update the KB, scan with the camera."""
        dust = self.world.has_dust(cell)
        new = self.safety.record_visit(cell, dust)
        storms = sorted(s for s in new if s.startswith("Storm_"))
        msg = f"enter {cell}" + (" dust!" if dust else "")
        if storms:
            msg += f" proved {', '.join(storms)}"
        self._log(msg)
        self.scan()

    def scan(self) -> None:
        """Thermal camera: finds the hiker with probability d(cell) if present."""
        self.scans += 1
        cell = self.pos
        d = self.world.detect_prob(cell)
        if cell == self.world.hiker and self.rng.random() < d:
            self.found = True
            self._log(f"HIKER FOUND at {cell}")
        else:
            self.belief = update_after_miss(self.belief, cell, d)

    def move_to(self, cell: Cell) -> None:
        if cell in self.world.storms:
            self.crashed = True
            self.pos = cell
            self.trail.append(cell)
            self._log(f"CRASH: flew into a sandstorm at {cell}")
            return
        self.battery -= self.world.cost(cell)
        self.pos = cell
        self.cells_flown += 1
        self.trail.append(cell)
        self._enter(cell)

    def hover_scan(self) -> None:
        self.battery -= 1
        self._log(f"scan again {self.pos}")
        self.scan()

    # ------------------------------------------------------------ YOUR CODE
    def plan_next_leg(self) -> List[Cell]:
        """Return the route to the next cell to scan, starting at self.pos.

        Steps:
          1. safe = self.safety.safe_cells()
          2. pick target = choose_search_cell(self.belief, self.world.detect_prob,
                 candidates = safe minus self.excluded,
                 travel_cost = manhattan distance from self.pos)
          3. if target is None: return []
          4. route = astar(GridProblem(self.world, self.pos, target, allowed=safe), manhattan)
          5. if no route: add target to self.excluded and go back to step 2
          6. return route.path   (a one-cell path [self.pos] means "scan here again")
        """
        # YOUR CODE HERE
        raise NotImplementedError("plan_next_leg() not implemented yet")

    # ------------------------------------------------------------ PROVIDED
    def search(self, on_step: Optional[Callable[["RescueDrone"], None]] = None) -> str:
        """Fly until the hiker is found, the drone crashes, or the battery is empty."""
        while not self.found and not self.crashed:
            path = self.plan_next_leg()
            if not path:
                return "no safe cell left to search"
            if path[0] != self.pos:
                raise ValueError("plan_next_leg() must start at the drone position")
            if len(path) == 1:
                if self.battery < 1:
                    return "battery empty"
                self.hover_scan()
            else:
                for cell in path[1:]:
                    if self.battery < self.world.cost(cell):
                        return "battery empty"
                    self.move_to(cell)
                    if on_step:
                        on_step(self)
                    if self.found or self.crashed:
                        break
        return "hiker found" if self.found else "drone crashed"

    def plan_delivery(self) -> PlanResult:
        """Phase 3 on this map: fuel per flight comes from A* route costs."""
        sites = {"Base": self.world.base, "Oasis": self.world.oasis, "Hiker": self.world.hiker}
        fuel_cost = delivery_fuel_costs(self.world, sites)
        return forward_astar(build_rescue_problem(fuel_cost))

    def report(self, reason: str, delivery: Optional[PlanResult] = None) -> MissionReport:
        return MissionReport(
            found=self.found, crashed=self.crashed, battery_left=self.battery,
            cells_flown=self.cells_flown, scans=self.scans,
            safe_cells=len(self.safety.safe_cells()),
            storms_proved=len(self.safety.storm_cells()),
            hiker_belief_at_end=self.belief.get(self.world.hiker, 0.0) if self.world.hiker else 0.0,
            delivery=delivery, reason=reason, frames=self.frames)


# ---------------------------------------------------------------- PROVIDED HELPERS
def delivery_fuel_costs(world: DesertMap, sites: Dict[str, Cell]) -> Dict[Tuple[str, str], int]:
    """Fuel units between every pair of sites: 1 if the A* route cost is at most
    FUEL_UNIT_THRESHOLD, else 2. (High-altitude flight: storms do not matter.)"""
    costs = {}
    for a, ca in sites.items():
        for b, cb in sites.items():
            if a == b:
                continue
            res = astar(GridProblem(world, ca, cb), manhattan)
            costs[(a, b)] = 1 if res.cost <= FUEL_UNIT_THRESHOLD else 2
    return costs


def run_mission(world: DesertMap, battery: float = DEFAULT_BATTERY,
                on_step: Optional[Callable[[RescueDrone], None]] = None) -> Tuple[RescueDrone, MissionReport]:
    drone = RescueDrone(world, battery)
    reason = drone.search(on_step)
    delivery = drone.plan_delivery() if drone.found else None
    return drone, drone.report(reason, delivery)


def explore_safely(world: DesertMap, moves: int = 60) -> RescueDrone:
    """Logic demo: always fly to the closest proved-safe cell not visited yet.
    No Bayes here - this only shows what your KB can prove."""
    drone = RescueDrone(world, battery=10 ** 6)
    for _ in range(moves):
        safe = drone.safety.safe_cells()
        todo = sorted(safe - drone.safety.visited,
                      key=lambda c: (manhattan(drone.pos, c), c))
        if not todo:
            break
        route = astar(GridProblem(world, drone.pos, todo[0], allowed=safe), manhattan)
        if not route.found:
            break
        for cell in route.path[1:]:
            drone.move_to(cell)
    return drone
