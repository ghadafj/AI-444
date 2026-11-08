"""Public tests for Phase 2 - Logic."""

from core.logic import KnowledgeBase, Rule, SafetyMap, percept_rules, sym
from world.desert_map import DesertMap


def test_tell_and_ask_fact():
    kb = KnowledgeBase()
    kb.tell_fact("Safe_0_0")
    assert kb.ask("Safe_0_0"), "a told fact must be provable"
    assert not kb.ask("Safe_9_9"), "an unknown symbol must not be provable"


def test_forward_chaining():
    kb = KnowledgeBase()
    kb.tell_fact("A")
    kb.tell_fact("C")
    kb.tell_rule(["A"], "B")
    kb.tell_rule(["B", "C"], "D")
    kb.tell_rule(["D", "E"], "F")
    new = kb.forward_chain()
    assert new == {"B", "D"}, f"forward_chain should return the NEW symbols {{'B','D'}}, got {new}"
    assert kb.ask("D"), "D follows from A, C and the rules"
    assert not kb.ask("F"), "F needs E, which is unknown"
    assert kb.forward_chain() == set(), "a second call has nothing new to prove"


def test_no_duplicate_rules():
    kb = KnowledgeBase()
    kb.tell_rule(["A", "B"], "C")
    kb.tell_rule(["B", "A"], "C")
    assert len(kb.rules) == 1, "the same rule (premise order does not matter) must be stored once"


def test_percept_no_dust():
    facts, rules = percept_rules((1, 1), False, [(0, 1), (1, 2)])
    assert set(facts) == {"Safe_1_1", "NoDust_1_1"}, f"wrong facts: {facts}"
    expected = {Rule(frozenset({"NoDust_1_1"}), "Safe_0_1"),
                Rule(frozenset({"NoDust_1_1"}), "Safe_1_2")}
    assert set(rules) == expected, f"wrong rules: {[str(r) for r in rules]}"


def test_percept_dust():
    facts, rules = percept_rules((1, 1), True, [(0, 1), (1, 2)])
    assert set(facts) == {"Safe_1_1", "Dust_1_1"}, f"wrong facts: {facts}"
    expected = {Rule(frozenset({"Dust_1_1", "Safe_1_2"}), "Storm_0_1"),
                Rule(frozenset({"Dust_1_1", "Safe_0_1"}), "Storm_1_2")}
    assert set(rules) == expected, f"wrong rules: {[str(r) for r in rules]}"


def test_drone_proves_a_storm():
    #  B . .      the drone visits (0,0), (0,1), (0,2)
    #  . S .      dust at (0,1); no dust at (0,0) and (0,2)
    #  . . .      => (1,1) must be the storm
    world = DesertMap.from_strings(["B..", ".S.", "..."])
    sm = SafetyMap(world)
    for cell in [(0, 0), (0, 1), (0, 2)]:
        sm.record_visit(cell, world.has_dust(cell))
    assert sm.is_safe((1, 0)) and sm.is_safe((1, 2)), "no-dust cells make their neighbours safe"
    assert sm.is_storm((1, 1)), "dust at (0,1) with all other neighbours safe proves Storm_1_1"
    assert not sm.is_safe((1, 1)), "a storm cell must never be proved safe"


def test_sound_on_generated_map():
    from agent.drone import explore_safely
    world = DesertMap.generate(444)
    drone = explore_safely(world, moves=80)
    assert not drone.crashed, "the drone flew into a storm: a cell was wrongly proved safe"
    wrong = drone.safety.storm_cells() - world.storms
    assert not wrong, f"cells proved to be storms that are not: {sorted(wrong)}"
    assert len(drone.safety.safe_cells()) > 40, "the KB should prove many cells safe"
