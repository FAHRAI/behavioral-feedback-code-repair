import json
from pathlib import Path

import pytest

from feedback_study import confirmatory

ROOT = Path(__file__).resolve().parents[1]
ROOTS = json.loads((ROOT / "data/confirmatory/roots.json").read_text())
MAIN = json.loads((ROOT / "data/main/costs.json").read_text())


@pytest.fixture(scope="module")
def result():
    return confirmatory.analyze(ROOTS, MAIN)


def pp(value):
    return round(100 * value, 2)


def test_state_and_repairs(result):
    assert result["roots"] == 1080
    assert result["state_roots"] == 150
    assert result["confirmatory"]["repaired_in_state"] == {"B": 18, "C": 40, "P": 20}
    assert len(result["confirmatory"]["state_clusters"]) == 8


def test_confirmatory_hypotheses(result):
    h1, h2 = result["confirmatory"]["H1_C_minus_B"], result["confirmatory"]["H2_C_minus_P"]
    assert (pp(h1["estimate"]), pp(h1["lower"]), pp(h1["upper"])) == (14.67, 5.36, 19.51)
    assert (pp(h2["estimate"]), pp(h2["lower"]), pp(h2["upper"])) == (13.33, 4.46, 20.0)
    assert h1["decision"] == h2["decision"] == "confirmed"
    assert (h1["x_only"], h1["y_only"]) == (25, 3)


def test_equal_cell_intervals_keep_cluster_multiplicity(result):
    cells = result["confirmatory"]["all_roots"]["equal_cell"]
    assert (pp(cells["C_minus_B"]["lower"]), pp(cells["C_minus_B"]["upper"])) == (-0.53, 4.44)
    assert (pp(cells["C_minus_P"]["lower"]), pp(cells["C_minus_P"]["upper"])) == (0.82, 6.17)


def test_signal_only_addendum(result):
    addendum = result["addendum"]
    assert addendum["repaired_in_state"]["Q"] == 42
    h3 = addendum["H3_C_minus_Q"]
    assert (pp(h3["estimate"]), pp(h3["lower"]), pp(h3["upper"])) == (-1.33, -2.97, 0.0)
    assert h3["decision"] == "not_confirmed"
    assert addendum["signal"]["length_matched"] is True
    assert addendum["signal"]["repetitions"] == [3, 25]


def test_costs(result):
    main, repeat = result["costs"]["main"], result["costs"]["confirmatory"]
    assert main["C_vs_B"]["extra_input_tokens"] == 125_388
    assert round(main["branches"]["B"]["usd"], 3) == 1.114
    assert round(main["branches"]["C"]["usd"], 3) == 1.288
    assert repeat["C_vs_B"]["extra_input_tokens"] == 157_108
    assert round(repeat["total_usd"], 2) == 6.27


def test_bootstrap_is_deterministic():
    state = [r for r in ROOTS if confirmatory.in_state(r)]
    statistic = confirmatory.mean_difference("C", "B")
    first = confirmatory.cluster_bootstrap(state, statistic, seed=1, replicates=200)
    assert first == confirmatory.cluster_bootstrap(state, statistic, seed=1, replicates=200)
