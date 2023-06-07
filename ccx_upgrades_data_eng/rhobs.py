"""Functions for generating the RHOBS queries needed by the service."""

import logging
from typing import List, Tuple
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import HTTPException

from ccx_upgrades_data_eng.auth import get_session_manager
from ccx_upgrades_data_eng.config import get_settings
from ccx_upgrades_data_eng.models import Alert, FOC, UpgradeRisksPredictors
import ccx_upgrades_data_eng.metrics as metrics

logger = logging.getLogger(__name__)


def single_cluster_alerts_and_focs(cluster_id: str) -> str:
    """Return a query for retrieving alerts and focs for just one cluster."""
    return alerts_and_focs([cluster_id])


def alerts_and_focs(cluster_ids: List[str]) -> str:
    """Return a query for retrieving alerts and focs for serveral clusters."""
    queries = []

    for cluster_id in cluster_ids:
        queries.append(
            f"""console_url{{_id="{cluster_id}"}}
or
alerts{{_id="{cluster_id}", namespace=~"openshift-.*", severity=~"warning|critical"}}
or
cluster_operator_conditions{{_id="{cluster_id}", condition="Available"}} == 0
or
cluster_operator_conditions{{_id="{cluster_id}", condition="Degraded"}} == 1"""
        )

    return "\nor\n".join(queries)


def perform_rhobs_request(cluster_id: UUID) -> Tuple[UpgradeRisksPredictors, str]:
    """
    Run the requests to RHOBS server and return the retrieved predictors.

    Also return the console url.
    """
    settings = get_settings()
    session = get_session_manager().get_session()

    rhobs_endpoint = f"/api/metrics/v1/{settings.rhobs_tenant}/api/v1/query"
    query = single_cluster_alerts_and_focs(cluster_id)

    response = session.get(
        f"{settings.rhobs_url}{rhobs_endpoint}",
        params={
            "query": query,
            "time": get_timestamp_minutes_before(settings.rhobs_query_max_minutes_for_data),
        },
        timeout=settings.rhobs_request_timeout,
        verify=not settings.allow_insecure,
    )

    if response.status_code == 404:
        logger.debug(f'cluster "{cluster_id}" not found in Observatorium')
        logger.debug("Observatorium response status code: %s", response.status_code)
        logger.debug("Observatorium response text: %s", response.text)
        raise HTTPException(status_code=404, detail="Cluster not found")

    elif response.status_code != 200:
        logger.debug("Observatorium response status code: %s", response.status_code)
        logger.debug("Observatorium response text: %s", response.text)
        raise HTTPException(status_code=response.status_code)

    results = response.json().get("data", dict()).get("result", list())
    logger.info("Observatorium response contains %s results", len(results))
    logger.debug("Observatorium request elapsed time: %s", response.elapsed.total_seconds())
    logger.debug("Observatorium response results: %s", results)
    metrics.update_ccx_upgrades_rhobs_time(response.elapsed.total_seconds())

    alerts = list()
    focs = list()

    console_url = ""

    for result in results:
        metric = result.get("metric")
        if not metric:
            logger.debug("result received with no metric: %s", result)
            continue

        if metric["__name__"] == "console_url":
            if "url" not in metric.keys():
                continue
            console_url = metric["url"]

        elif metric["__name__"] == "alerts":
            alerts.append(Alert.parse_metric(metric))

        elif metric["__name__"] == "cluster_operator_conditions":
            focs.append(FOC.parse_metric(metric))

        else:
            logger.debug("received a metric from unexpected type: %s", metric["__name__"])

    predictors = UpgradeRisksPredictors(alerts=alerts, operator_conditions=focs)

    logger.debug(
        f"Before removing duplicates: {len(predictors.alerts)} alerts and {len(predictors.operator_conditions)} for cluster {cluster_id}"
    )
    predictors.remove_duplicates()
    logger.debug(
        f"After removing duplicates: {len(predictors.alerts)} alerts and {len(predictors.operator_conditions)} for cluster {cluster_id}"
    )

    return predictors, console_url


def get_timestamp_minutes_before(minutes):
    """Return the timestamp $hours_before."""
    d = datetime.now() - timedelta(minutes=minutes)
    return d.timestamp()
