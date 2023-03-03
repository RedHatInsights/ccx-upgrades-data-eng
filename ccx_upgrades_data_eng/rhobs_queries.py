"""Functions for generating the RHOBS queries needed by the service."""

from typing import List


def single_cluster_alerts_and_focs(cluster_id: str) -> str:
    """Return a query for retrieving alerts and focs for just one cluster."""
    return alerts_and_focs([cluster_id])


def alerts_and_focs(cluster_ids: List[str]) -> str:
    """Return a query for retrieving alerts and focs for serveral clusters."""
    queries = []

    for cluster_id in cluster_ids:
        queries.append(
            f"""alerts{{_id="{cluster_id}", namespace=~"openshift-.*", severity=~"warning|critical"}}
or
cluster_operator_conditions{{_id="{cluster_id}", condition="Available"}} == 0
or
cluster_operator_conditions{{_id="{cluster_id}", condition="Degraded"}} == 1"""
        )

    return "\nor\n".join(queries)
