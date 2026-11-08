"""
Desert Rescue Drone - SE 444 Course Project (Fall 2026)

Run tests:
    python main.py --test search        (or warmup, logic, planning, bayes, mission, all)

Run your agent on YOUR map (your student ID is the map seed):
    python main.py --id 123456 --show
    python main.py --id 123456 --phase warmup
    python main.py --id 123456 --phase search
    python main.py --id 123456 --phase logic
    python main.py --id 123456 --phase planning
    python main.py --id 123456 --phase bayes
    python main.py --id 123456 --phase mission --gui
    python main.py --id 123456 --phase mission --save mission.png
"""

from __future__ import annotations

import argparse
import sys
import time


def show_map(world) -> None:
    print(world.to_ascii())
    print("\nLegend: . sand(1)  r rocks(2)  d dunes(3)  # mountain  B base  O oasis  L last phone signal")
    print(f"Base {world.base}   Oasis {world.oasis}   Last signal {world.last_signal}")
    print("Sandstorms and the hiker are hidden. Your drone must find them.")


def phase_warmup(world) -> None:
    from core.warmup import cheapest_neighbour, count_terrain
    from world.desert_map import TERRAIN_NAME
    counts = count_terrain(world)
    print("Task 0 - cells of each terrain on your map\n")
    for letter, name in TERRAIN_NAME.items():
        print(f"  {name:<9} '{letter}'  {counts.get(letter, 0):>4}")
    print(f"  {'total':<14}{sum(counts.values()):>4}  (= {world.rows} x {world.cols})")
    print(f"\nCheapest first step from the base {world.base}: {cheapest_neighbour(world, world.base)}")


def phase_search(world) -> None:
    from core.search import GridProblem, astar, bfs, euclidean, manhattan, ucs
    print("Route from Base to the last phone signal\n")
    print(f"{'algorithm':<22}{'moves':>7}{'cost':>8}{'expanded':>10}")
    rows = [("BFS", lambda p: bfs(p)), ("UCS", lambda p: ucs(p)),
            ("A* (manhattan)", lambda p: astar(p, manhattan)),
            ("A* (euclidean)", lambda p: astar(p, euclidean))]
    best = None
    for name, algo in rows:
        p = GridProblem(world, world.base, world.last_signal)
        t = time.perf_counter()
        r = algo(p)
        ms = (time.perf_counter() - t) * 1000
        print(f"{name:<22}{len(r.path) - 1:>7}{r.cost:>8.0f}{r.expanded:>10}   ({ms:.1f} ms)")
        if name == "A* (manhattan)":
            best = r
    if best and best.found:
        print("\nA* route (*):\n")
        print(world.to_ascii({c: "*" for c in best.path[1:-1]}))


def phase_logic(world) -> None:
    from agent.drone import explore_safely
    drone = explore_safely(world, moves=80)
    safe, storms = drone.safety.safe_cells(), drone.safety.storm_cells()
    print(f"Visited {len(drone.safety.visited)} cells, proved {len(safe)} safe, {len(storms)} storm(s)")
    print(f"Facts in KB: {len(drone.safety.kb.facts)}   Rules in KB: {len(drone.safety.kb.rules)}")
    if drone.crashed:
        print("!! The drone CRASHED: your KB proved a storm cell safe. Check percept_rules().")
    marks = {c: "+" for c in safe}
    marks.update({c: "X" for c in storms})
    marks.update({c: "v" for c in drone.safety.visited})
    print("\nv visited   + proved safe   X proved storm\n")
    print(world.to_ascii(marks))
    for f in sorted(s for s in drone.safety.kb.facts if s.startswith("Storm_")):
        print("  proved:", f)


def phase_planning(world) -> None:
    from agent.drone import delivery_fuel_costs
    from core.planning import build_rescue_problem, check_plan, forward_astar, forward_bfs
    # The hiker position is hidden until found; for this demo we use the true one.
    print("(Demo: uses the true hiker cell. In the mission the drone plans after finding the hiker.)\n")
    sites = {"Base": world.base, "Oasis": world.oasis, "Hiker": world.hiker}
    costs = delivery_fuel_costs(world, sites)
    print("Fuel units per flight (from A* route costs on your map):")
    for (a, b), c in sorted(costs.items()):
        print(f"  {a:>5} -> {b:<5}: {c}")
    prob = build_rescue_problem(costs)
    print(f"\nGround actions: {len(prob.actions)}")
    for name, planner in (("Forward BFS", forward_bfs), ("Forward A* (goal count)", forward_astar)):
        t = time.perf_counter()
        res = planner(prob)
        ms = (time.perf_counter() - t) * 1000
        print(f"\n{name}: expanded {res.expanded} states in {ms:.1f} ms")
        if not res.found:
            print("  no plan found")
            continue
        ok, msg = check_plan(prob, res.plan)
        for i, a in enumerate(res.plan, 1):
            print(f"  {i:>2}. {a.name}")
        print(f"  check: {msg}")


def phase_bayes(world) -> None:
    from core.bayes import entropy_bits, most_likely, normalize, update_after_miss
    belief = normalize(world.hiker_prior())
    print(f"Prior: uncertainty {entropy_bits(belief):.2f} bits. Most likely cells:")
    for c, p in most_likely(belief):
        print(f"  {c}  {p:.4f}  ({world.terrain(c)})")
    print("\nScan the cell with the best chance belief*d, 10 times (pretend every scan misses):")
    for i in range(10):
        c = max(belief, key=lambda x: (belief[x] * world.detect_prob(x), x))
        before = belief[c]
        belief = update_after_miss(belief, c, world.detect_prob(c))
        print(f"  scan {i + 1:>2}: {c} d={world.detect_prob(c):.1f}  "
              f"belief {before:.4f} -> {belief[c]:.4f}   total={sum(belief.values()):.6f}")
    print(f"\nAfter 10 misses: uncertainty {entropy_bits(belief):.2f} bits")


def phase_mission(world, gui: bool, save: str | None, battery: float) -> None:
    from agent.drone import run_mission
    viewer = None
    if gui or save:
        try:
            from viz.viewer import Viewer
            viewer = Viewer(world, headless=not gui)
        except ImportError:
            print("pygame is not installed: pip install pygame   (continuing in text mode)")

    def on_step(drone):
        if viewer and gui:
            viewer.draw(drone)
            if not viewer.tick(12):
                sys.exit(0)

    drone, rep = run_mission(world, battery, on_step)
    print(f"Result: {rep.reason}")
    print(f"  cells flown {rep.cells_flown}, scans {rep.scans}, battery left {rep.battery_left:.0f}")
    print(f"  proved safe {rep.safe_cells}, proved storms {rep.storms_proved}")
    print(f"  true hiker cell {world.hiker}, final belief there {rep.hiker_belief_at_end:.3f}")
    if rep.delivery and rep.delivery.found:
        print(f"\nDelivery plan ({len(rep.delivery.plan)} actions):")
        for i, a in enumerate(rep.delivery.plan, 1):
            print(f"  {i:>2}. {a.name}")
    marks = {c: "~" for c in drone.trail}
    marks.update({c: "S" for c in world.storms})
    if world.hiker:
        marks[world.hiker] = "H"
    print("\n~ drone trail   S sandstorm (revealed)   H hiker\n")
    print(world.to_ascii(marks))
    if viewer:
        viewer.draw(drone, reveal=True, status=rep.reason)
        if save:
            viewer.save(save)
            print(f"\nSaved picture to {save}")
        if gui:
            viewer.wait_for_close()


def main() -> None:
    ap = argparse.ArgumentParser(description="SE 444 Desert Rescue Drone")
    ap.add_argument("--test", choices=["warmup", "search", "logic", "planning", "bayes", "mission", "all"])
    ap.add_argument("--id", help="your student ID (the seed of your personal map)")
    ap.add_argument("--show", action="store_true", help="print your map")
    ap.add_argument("--phase", choices=["warmup", "search", "logic", "planning", "bayes", "mission"])
    ap.add_argument("--gui", action="store_true", help="animate the mission with pygame")
    ap.add_argument("--save", help="save a PNG of the final mission state")
    ap.add_argument("--battery", type=float, default=None, help="mission battery (default 600)")
    args = ap.parse_args()

    if args.test:
        from tests.harness import run
        sys.exit(0 if run(args.test) else 1)

    if not args.id:
        ap.error("give your student ID with --id, or run tests with --test")

    from world.desert_map import DesertMap, seed_from_student_id
    world = DesertMap.generate(seed_from_student_id(args.id))
    print(f"=== Desert Rescue Drone | map of student {args.id} ===\n")

    if args.show or not args.phase:
        show_map(world)
    if args.phase == "warmup":
        phase_warmup(world)
    elif args.phase == "search":
        phase_search(world)
    elif args.phase == "logic":
        phase_logic(world)
    elif args.phase == "planning":
        phase_planning(world)
    elif args.phase == "bayes":
        phase_bayes(world)
    elif args.phase == "mission":
        from agent.drone import DEFAULT_BATTERY
        phase_mission(world, args.gui, args.save, args.battery or DEFAULT_BATTERY)


if __name__ == "__main__":
    main()
