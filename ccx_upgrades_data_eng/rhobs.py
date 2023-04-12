"""Functions for generating the RHOBS queries needed by the service."""

import logging
from typing import List
from uuid import UUID

from fastapi import HTTPException

from ccx_upgrades_data_eng.auth import get_session_manager
from ccx_upgrades_data_eng.config import get_settings
from ccx_upgrades_data_eng.models import Alert, FOC, UpgradeRisksPredictors


logger = logging.getLogger(__name__)


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


def perform_rhobs_request(cluster_id: UUID) -> UpgradeRisksPredictors:
    """Run the requests to RHOBS server and return the retrieved predictors."""
    settings = get_settings()
    session = get_session_manager().get_session()

    rhobs_endpoint = f"/api/metrics/v1/{settings.rhobs_tenant}/api/v1/query"
    query = single_cluster_alerts_and_focs(cluster_id)

    response = session.get(
        f"{settings.rhobs_url}{rhobs_endpoint}",
        params={"query": query},
        timeout=settings.rhobs_request_timeout,
        verify=not settings.allow_insecure,
    )

    if response.status_code == 404:
        logger.debug(f'cluster "{cluster_id}" not found in Observatorium')
        raise HTTPException(status_code=404, detail="Cluster not found")

    elif response.status_code != 200:
        logger.debug("Observatorium response status code:", response.status_code)
        logger.debug("Observatorium response text:", response.text)
        raise HTTPException(status_code=response.status_code)

    results = response.json().get("data", dict()).get("result", list())
    logger.info("Observatorium response contains %s results", len(results))
    logger.debug("Observatorium request elapsed time: %s", response.elapsed.total_seconds())
    logger.debug("Observatorium response results: %s", results)

    alerts = list()
    focs = list()

    for result in results:
        metric = result.get("metric")
        if not metric:
            logger.debug("result received with no metric: %s", result)
            continue

        if metric["__name__"] == "alerts":
            alerts.append(Alert.parse_metric(metric))

        elif metric["__name__"] == "cluster_operator_conditions":
            focs.append(FOC.parse_obj(metric))

        else:
            logger.debug("received a metric from unexpected type: %s", metric["__name__"])

    return UpgradeRisksPredictors(alerts=alerts, operator_conditions=focs)
