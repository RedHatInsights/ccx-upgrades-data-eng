"""Functions for generating the RHOBS queries needed by the service."""

from typing import List


def single_cluster_alerts_and_focs(cluster_id: str) -> str:
    """Returns a query for retrieving alerts and focs for just one cluster."""
    return alerts_and_focs([cluster_id])


def alerts_and_focs(cluster_ids: List[str]) -> str:
    """Returns a query for retrieving alerts and focs for serveral clusters."""

    queries = list()

    for cluster_id in cluster_ids:
        queries.append(
            f"""alerts{{_id="{cluster_id}"}}
or
cluster_operator_conditions{{_id="{cluster_id}"}}"""
        )
    
    return "\nor\n".join(queries)
