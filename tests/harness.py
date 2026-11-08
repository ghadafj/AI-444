"""Tiny test runner (no extra packages needed). PROVIDED."""

from __future__ import annotations

import importlib
import traceback
from typing import Callable, List, Tuple

PHASES = ["warmup", "search", "logic", "planning", "bayes", "mission"]

GREEN, RED, YELLOW, END = "\033[92m", "\033[91m", "\033[93m", "\033[0m"


def run_phase(phase: str) -> Tuple[int, int]:
    module = importlib.import_module(f"tests.test_{phase}")
    tests: List[Tuple[str, Callable[[], None]]] = [
        (name[5:], fn) for name, fn in vars(module).items()
        if name.startswith("test_") and callable(fn)]
    print(f"\n=== Phase: {phase} ({len(tests)} tests) ===")
    passed = 0
    for name, fn in tests:
        try:
            fn()
        except NotImplementedError as e:
            print(f"  {YELLOW}TODO{END}  {name}: {e}")
        except AssertionError as e:
            print(f"  {RED}FAIL{END}  {name}: {e}")
        except Exception:  # noqa: BLE001 - show the student their crash
            print(f"  {RED}ERROR{END} {name}:")
            print("        " + traceback.format_exc().strip().replace("\n", "\n        "))
        else:
            passed += 1
            print(f"  {GREEN}PASS{END}  {name}")
    print(f"  -> {passed}/{len(tests)} passed")
    return passed, len(tests)


def run(phase: str) -> bool:
    phases = PHASES if phase == "all" else [phase]
    total_p = total_n = 0
    for p in phases:
        a, b = run_phase(p)
        total_p += a
        total_n += b
    if len(phases) > 1:
        print(f"\nTOTAL: {total_p}/{total_n} public tests passed")
    print("Note: these are the PUBLIC tests. Grading also uses hidden tests on your own map.")
    return total_p == total_n
