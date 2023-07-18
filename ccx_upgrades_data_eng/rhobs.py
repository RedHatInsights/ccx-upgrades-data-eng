"""Functions for generating the RHOBS queries needed by the service."""

import logging
from typing import List, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import requests

from cachetools import cached
from fastapi import HTTPException

from ccx_upgrades_data_eng.auth import get_session_manager
from ccx_upgrades_data_eng.config import get_settings
import ccx_upgrades_data_eng.metrics as metrics
from ccx_upgrades_data_eng.models import (
    Alert,
    FOC,
    UpgradeRisksPredictors,
)
from ccx_upgrades_data_eng.utils import CustomTTLCache

logger = logging.getLogger(__name__)


def alerts_and_focs(cluster_ids: List[str]) -> str:
    """Return a query for retrieving alerts and focs for serveral clusters."""
    clusters = "|".join(cluster_ids)
    return f"""console_url{{_id=~"{clusters}"}}
or
alerts{{_id=~"{clusters}", namespace=~"openshift-.*", severity=~"warning|critical"}}
or
cluster_operator_conditions{{_id=~"{clusters}", condition="Available"}} == 0
or
cluster_operator_conditions{{_id=~"{clusters}", condition="Degraded"}} == 1"""


def query_rhobs_endpoint(query: str) -> requests.Response:
    """Request the RHOBS  for a given cluster ID."""
    settings = get_settings()
    session = get_session_manager().get_session()

    rhobs_endpoint = f"/api/metrics/v1/{settings.rhobs_tenant}/api/v1/query"

    return session.get(
        f"{settings.rhobs_url}{rhobs_endpoint}",
        params={
            "query": query,
            "time": get_timestamp_minutes_before(settings.rhobs_query_max_minutes_for_data),
        },
        timeout=settings.rhobs_request_timeout,
        verify=not settings.allow_insecure,
    )


@cached(cache=CustomTTLCache())
def perform_rhobs_request(cluster_id: UUID) -> Tuple[UpgradeRisksPredictors, str]:
    """
    Run the requests to RHOBS server and return the retrieved predictors.

    Also return the console url.
    """
    query = alerts_and_focs([cluster_id])
    response = query_rhobs_endpoint(query)

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

    alerts = set()
    focs = set()

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
            alerts.add(Alert.parse_metric(metric))

        elif metric["__name__"] == "cluster_operator_conditions":
            focs.add(FOC.parse_metric(metric))

        else:
            logger.debug("received a metric from unexpected type: %s", metric["__name__"])

    predictors = UpgradeRisksPredictors(alerts=list(alerts), operator_conditions=list(focs))

    return predictors, console_url


def get_timestamp_minutes_before(minutes):
    """Return the timestamp $hours_before."""
    d = datetime.now() - timedelta(minutes=minutes)
    return d.timestamp()


if __name__ == "__main__":
    from data import clusters  # fill this with a list of clusters
    import time
    import random

    query = alerts_and_focs([clusters[0]])
    resp = query_rhobs_endpoint(query)
    print("n_clusters,duration,n_alerts,size")
    for N in range(10, 510, 20):
        clusters_to_test = random.sample(clusters, N)
        query = alerts_and_focs(clusters_to_test)
        start_time = time.time()
        resp = query_rhobs_endpoint(query)
        duration = time.time() - start_time
        assert resp.status_code == 200, f"{resp.status_code}: {resp.text}"
        results = resp.json().get("data", dict()).get("result", list())
        assert len(results) > 5
        print(f"{len(clusters_to_test)},{duration},{len(results)},{len(resp.content)}")
        time.sleep(1)
