"""Public tests for Phase 5 - the full mission."""

from agent.drone import RescueDrone, run_mission
from world.desert_map import DesertMap


def test_next_leg_is_safe_and_connected():
    world = DesertMap.generate(444)
    drone = RescueDrone(world)
    for _ in range(15):
        path = drone.plan_next_leg()
        assert path, "plan_next_leg() returned nothing at the start of the mission"
        assert path[0] == drone.pos, "the leg must start at the drone position"
        safe = drone.safety.safe_cells()
        for a, b in zip(path, path[1:]):
            assert b in world.neighbors(a), f"illegal move {a} -> {b}"
            assert b in safe, f"the leg goes through {b}, which is not proved safe"
        for cell in path[1:]:
            drone.move_to(cell)
        if drone.found:
            break


def test_full_mission_runs():
    world = DesertMap.generate(444)
    drone, report = run_mission(world)
    assert not report.crashed, "the drone must never crash: it only flies over proved-safe cells"
    assert report.found, f"on map 444 the hiker should be found (stopped: {report.reason})"
    assert report.delivery and report.delivery.found, "a delivery plan must be found"
