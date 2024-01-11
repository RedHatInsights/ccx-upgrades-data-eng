"""Definition of the REST API for the inference service."""

import logging
from typing import List
from uuid import UUID

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse

from ccx_upgrades_data_eng.auth import get_session_manager, SessionManagerException, TokenException
from ccx_upgrades_data_eng.config import get_settings, Settings
from ccx_upgrades_data_eng.inference import get_filled_inference_for_predictors
from ccx_upgrades_data_eng.models import ClustersList, UpgradeApiResponse
from ccx_upgrades_data_eng.rhobs import perform_rhobs_request
import ccx_upgrades_data_eng.metrics as metrics

from prometheus_fastapi_instrumentator import Instrumentator


logger = logging.getLogger(__name__)
app = FastAPI()


@app.on_event("startup")
async def expose_metrics():
    """Expose the prometheus metrics in the /metrics endpoint."""
    logger.debug("Exposing metrics")
    Instrumentator().instrument(app).expose(app)
    logger.info("Metrics available at /metrics")


@app.middleware("http")  # Check if it needs to be refreshed in each request
# @repeat_every(seconds=360)  # Refresh the, default expires_at is 9 min
async def refresh_sso_token(request: Request, call_next) -> JSONResponse:
    """Initialize the session manager (if needed) and refresh the token (if needed)."""
    try:
        # this is cached (if initialized correctly before) so it will be
        # initialized just once
        session_manager = get_session_manager()
        session_manager.refresh_token()
    except SessionManagerException as ex:
        logger.error("Unable to initialize SSO session: %s", ex)
        return JSONResponse(
            "Unable to initialize SSO session", status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    except TokenException as ex:
        logger.error("Unable to update SSO token: %s", ex)
        return JSONResponse(
            "Unable to update SSO token", status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    return await call_next(request)


@app.get("/cluster/{cluster_id}/upgrade-risks-prediction", response_model=UpgradeApiResponse)
async def upgrade_risks_prediction(cluster_id: UUID, settings: Settings = Depends(get_settings)):
    """Return the predition of an upgrade failure given a set of alerts and focs."""
    logger.info(f"Received cluster: {cluster_id}")
    logger.debug("Getting predictors from RHOBS")
    predictors, console_url = perform_rhobs_request(cluster_id)
    if console_url == "":
        return JSONResponse("No data for this cluster", status_code=status.HTTP_404_NOT_FOUND)

    logger.debug("Getting inference result")
    inference_result = get_filled_inference_for_predictors(predictors, console_url)

    metrics.update_ccx_upgrades_prediction_total(inference_result)
    metrics.update_ccx_upgrades_risks_total(inference_result)

    return inference_result


@app.post("/upgrade-risks-prediction")
async def upgrade_risks_multi_cluster_predictions(clusters_list: ClustersList, settings: Settings = Depends(get_settings)):
    """Return the upgrade risks predictions for the provided clusters."""

    for cluster_id in clusters_list.clusters:
        logger.info(f"Received cluster: {cluster_id}")
        logger.debug("Getting predictors from RHOBS")
