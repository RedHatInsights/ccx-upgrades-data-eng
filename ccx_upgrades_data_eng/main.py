"""Definition of the REST API for the inference service."""

import logging
import os
from uuid import UUID

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse

from ccx_upgrades_data_eng.auth import (
    get_session_manager,
    SessionManagerException,
    TokenException,
)
from ccx_upgrades_data_eng.config import get_settings, Settings
from ccx_upgrades_data_eng.inference import get_filled_inference_for_predictors
from ccx_upgrades_data_eng.models import (
    ClustersList,
    ClusterPrediction,
    MultiClusterUpgradeApiResponse,
    UpgradeApiResponse,
)
from ccx_upgrades_data_eng.rhobs import (
    perform_rhobs_request,
    perform_rhobs_request_multi_cluster,
)
from ccx_upgrades_data_eng.sentry import init_sentry
import ccx_upgrades_data_eng.metrics as metrics

from prometheus_fastapi_instrumentator import Instrumentator
from ccx_upgrades_data_eng.utils import retry_with_exponential_backoff

logger = logging.getLogger(__name__)
app = FastAPI()

init_sentry(os.environ.get("SENTRY_DSN", None), None, os.environ.get("SENTRY_ENVIRONMENT", None))


@app.on_event("startup")
async def expose_metrics():
    """Expose the prometheus metrics in the /metrics endpoint."""
    logger.debug("Exposing metrics")
    Instrumentator().instrument(app).expose(app)
    logger.info("Metrics available at /metrics")


@retry_with_exponential_backoff(max_attempts=5, base_delay=1, max_delay=30)
async def get_session_and_refresh_token():
    """Initialize the session manager and refresh the token."""
    session_manager = get_session_manager()
    session_manager.refresh_token()


@app.middleware("http")
async def refresh_sso_token(request: Request, call_next) -> JSONResponse:
    """Middleware to ensure SSO token is refreshed before processing the request."""
    try:
        await get_session_and_refresh_token()
    except SessionManagerException as ex:
        logger.error("Unable to initialize SSO session: %s", ex)
        return JSONResponse(
            "Unable to initialize SSO session",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    except TokenException as ex:
        logger.error("Unable to update SSO token: %s", ex)
        return JSONResponse(
            "Unable to update SSO token",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return await call_next(request)


@app.get("/cluster/{cluster_id}/upgrade-risks-prediction", response_model=UpgradeApiResponse)
async def upgrade_risks_prediction(cluster_id: UUID, settings: Settings = Depends(get_settings)):
    """Return the predition of an upgrade failure given a set of alerts and focs."""
    logger.info(f"Received cluster: {cluster_id}")
    logger.debug("Getting predictors from RHOBS")
    predictors, console_url = perform_rhobs_request(cluster_id)

    if console_url is None or console_url == "":
        return JSONResponse("No data for this cluster", status_code=status.HTTP_404_NOT_FOUND)

    logger.debug("Getting inference result")
    inference_result = get_filled_inference_for_predictors(predictors, console_url)

    metrics.update_ccx_upgrades_prediction_total(inference_result)
    metrics.update_ccx_upgrades_risks_total(inference_result)

    return inference_result


@app.post("/upgrade-risks-prediction", response_model=MultiClusterUpgradeApiResponse)
async def upgrade_risks_multi_cluster_predictions(
    clusters_list: ClustersList, settings: Settings = Depends(get_settings)
):
    """Return the upgrade risks predictions for the provided clusters."""
    logger.info("Received clusters list: %s", clusters_list)
    logger.debug("Getting predictors from RHOBS or cache")
    predictors_per_cluster = perform_rhobs_request_multi_cluster(clusters_list.clusters)

    results = list()
    for cluster, prediction in predictors_per_cluster.items():
        inference_result = get_filled_inference_for_predictors(prediction[0], prediction[1])
        results.append(
            ClusterPrediction(
                cluster_id=str(cluster),
                prediction_status="ok",
                upgrade_recommended=inference_result.upgrade_recommended,
                upgrade_risks_predictors=inference_result.upgrade_risks_predictors,
                last_checked_at=inference_result.last_checked_at,
            ),
        )
        metrics.update_ccx_upgrades_prediction_total(inference_result)
        metrics.update_ccx_upgrades_risks_total(inference_result)

    for cluster in clusters_list.clusters:
        if cluster in predictors_per_cluster:
            continue

        results.append(
            ClusterPrediction(
                cluster_id=str(cluster),
                prediction_status="No data for the cluster",
            )
        )

    return MultiClusterUpgradeApiResponse(predictions=results)
