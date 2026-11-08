"""Public tests for Phase 4 - Probability."""

from core.bayes import choose_search_cell, detection_chance, normalize, update_after_miss

A, B, C = (0, 0), (0, 1), (0, 2)


def _close(x, y, tol=1e-9):
    return abs(x - y) < tol


def test_normalize():
    b = normalize({A: 2.0, B: 6.0, C: 2.0})
    assert _close(b[B], 0.6) and _close(sum(b.values()), 1.0), f"got {b}"
    try:
        normalize({A: 0.0})
    except ValueError:
        pass
    else:
        raise AssertionError("normalize must raise ValueError when all weights are 0")


def test_update_after_miss_numbers():
    prior = {A: 0.5, B: 0.3, C: 0.2}
    post = update_after_miss(prior, A, 0.8)
    # P(miss) = 1 - 0.5*0.8 = 0.6
    assert _close(post[A], 0.5 * 0.2 / 0.6), f"belief[A] should be {0.5*0.2/0.6:.4f}, got {post[A]:.4f}"
    assert _close(post[B], 0.5), f"belief[B] should be 0.5, got {post[B]:.4f}"
    assert _close(post[C], 0.2 / 0.6), f"belief[C] should be {0.2/0.6:.4f}, got {post[C]:.4f}"
    assert _close(sum(post.values()), 1.0), "the new belief must sum to 1"
    assert prior == {A: 0.5, B: 0.3, C: 0.2}, "update_after_miss must not change its input"


def test_perfect_camera_clears_cell():
    post = update_after_miss({A: 0.5, B: 0.5}, A, 1.0)
    assert _close(post[A], 0.0) and _close(post[B], 1.0), f"got {post}"


def test_two_misses_in_a_row():
    prior = {A: 0.4, B: 0.6}
    twice = update_after_miss(update_after_miss(prior, A, 0.5), A, 0.5)
    # same as one miss with a camera that misses with probability 0.5 * 0.5
    once = update_after_miss(prior, A, 1 - 0.25)
    assert _close(twice[A], once[A]), "two misses must equal one miss with (1-d)^2"


def test_detection_chance():
    assert _close(detection_chance({A: 0.4}, A, 0.5), 0.2)
    assert _close(detection_chance({A: 0.4}, B, 0.5), 0.0), "unknown cells have belief 0"


def test_choose_search_cell():
    belief = {A: 0.30, B: 0.40, C: 0.30}
    d = {A: 0.9, B: 0.5, C: 0.9}
    travel = {A: 0, B: 0, C: 4}
    # scores: A 0.27/1 = 0.27, B 0.20/1 = 0.20, C 0.27/5 = 0.054
    got = choose_search_cell(belief, d.get, [A, B, C], travel.get)
    assert got == A, f"expected {A}, got {got}"
    assert choose_search_cell(belief, d.get, [], travel.get) is None, "no candidates -> None"
    # tie between A and C when travel is equal -> smaller tuple wins
    got = choose_search_cell(belief, d.get, [C, A], lambda c: 0)
    assert got == A, f"ties must go to the smaller cell, got {got}"
