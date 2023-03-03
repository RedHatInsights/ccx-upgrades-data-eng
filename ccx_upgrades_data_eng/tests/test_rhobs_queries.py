"""Tests for the rhobs_queries module."""

from ccx_upgrades_data_eng.rhobs_queries import alerts_and_focs, single_cluster_alerts_and_focs


def test_single_cluster_alerts_and_focs():
    """Test if single_cluster_alerts_and_focs returns the expected query."""
    assert (
        single_cluster_alerts_and_focs("test")
        == """alerts{_id="test", namespace=~"openshift-.*", severity=~"warning|critical"}
or
cluster_operator_conditions{_id="test", condition="Available"} == 0
or
cluster_operator_conditions{_id="test", condition="Degraded"} == 1"""
    )


def test_multi_cluster_alerts_and_focs():
    """Test if alerts_and_focs returns the expected query."""
    assert (
        alerts_and_focs(["test1", "test2"])
        == """alerts{_id="test1", namespace=~"openshift-.*", severity=~"warning|critical"}
or
cluster_operator_conditions{_id="test1", condition="Available"} == 0
or
cluster_operator_conditions{_id="test1", condition="Degraded"} == 1
or
alerts{_id="test2", namespace=~"openshift-.*", severity=~"warning|critical"}
or
cluster_operator_conditions{_id="test2", condition="Available"} == 0
or
cluster_operator_conditions{_id="test2", condition="Degraded"} == 1"""
    )
