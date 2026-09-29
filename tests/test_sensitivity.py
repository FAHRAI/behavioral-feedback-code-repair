import math
from statistics import mean, variance

import pytest

from feedback_study.sensitivity import bootstrap, cr2, selected_mean, t_critical


@pytest.mark.parametrize(
    "df,expected",
    [
        (1, math.tan(math.pi * 0.475)),
        (2, math.sqrt(2 * 0.95**2 / (1 - 0.95**2))),
        (15, 2.131449545559323),
    ],
)
def test_t_quantiles_against_closed_forms_and_reference(df, expected):
    assert t_critical(df) == pytest.approx(expected, abs=2e-10)


def test_equal_cluster_cr2_reduces_to_t_on_cluster_means():
    means = [-0.2, 0.1, 0.3, 0.4]
    values = {2 * g + i: v for g, v in enumerate(means) for i in range(2)}
    clusters = {g: [2 * g, 2 * g + 1] for g in range(4)}
    result = cr2(values, clusters)
    assert result["estimate"] == pytest.approx(mean(means))
    assert result["variance"] == pytest.approx(variance(means) / 4)
    assert result["df_satterthwaite"] == pytest.approx(3)


def test_unequal_clusters_preserve_task_weighting_not_cluster_weighting():
    values = {0: 0, 1: 1, 2: 1, 3: 1}
    clusters = {"a": [0], "b": [1, 2, 3]}
    assert selected_mean(values, clusters, ["a", "b"]) == 0.75
    assert cr2(values, clusters)["estimate"] == 0.75
    assert selected_mean(values, clusters, ["a", "a", "b"]) == 0.6
    # Ratio-bootstrap need not be centered exactly at the empirical mean.
    draws = [selected_mean(values, clusters, [a, b]) for a in clusters for b in clusters]
    assert mean(draws) == 0.625


def test_null_contrast_is_degenerate_not_evidence_of_equivalence():
    values = {0: 0, 1: 0, 2: 0}
    clusters = {0: [0], 1: [1, 2]}
    assert cr2(values, clusters)["interval_95"] == [0, 0]
    assert bootstrap(values, clusters, seed=1, replicates=30)["interval_95"] == [0, 0]


def test_resampling_whole_task_does_not_independently_resample_paired_arms():
    # Opposite repeat differences cancel within each task; stored means stay zero.
    values = {0: mean([-1, 1]), 1: mean([1, -1])}
    assert bootstrap(values, {0: [0], 1: [1]}, seed=9, replicates=100)["interval_95"] == [0, 0]


def test_cr2_rejects_overlapping_clusters():
    with pytest.raises(ValueError, match="partition"):
        cr2({0: 1, 1: 0}, {"a": [0, 1], "b": [1]})


def test_bootstrap_is_reproducible():
    values = {0: -0.2, 1: 0.1, 2: 0.7}
    clusters = {0: [0], 1: [1, 2]}
    assert bootstrap(values, clusters, seed=123, replicates=200) == bootstrap(
        values, clusters, seed=123, replicates=200
    )
