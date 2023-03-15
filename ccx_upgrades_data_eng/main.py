"""Definition of the REST API for the inference service."""

import logging
from uuid import UUID

from fastapi import Depends, FastAPI
from fastapi_utils.tasks import repeat_every

from ccx_upgrades_data_eng.auth import get_session_manager
from ccx_upgrades_data_eng.config import get_settings, Settings
from ccx_upgrades_data_eng.inference import get_inference_for_predictors
from ccx_upgrades_data_eng.models import UpgradeApiResponse
from ccx_upgrades_data_eng.rhobs import perform_rhobs_request

from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger(__name__)
app = FastAPI()


@app.on_event("startup")
async def expose_metrics():
    """Expose the prometheus metrics in the /metrics endpoint."""
    logger.debug("Exposing metrics")
    Instrumentator().instrument(app).expose(app)
    logger.info("Metrics available at /metrics")


@app.on_event("startup")
def init_session_manager() -> None:
    """Force Oauth2Manager to refresh its token periodically."""
    logger.debug("Initializing the session manager")
    session_manager = get_session_manager()
    logger.debug("Refreshing the token")
    session_manager.refresh_token()


@app.on_event("startup")
@repeat_every(seconds=360)  # repeat every 6 minutes, default expires_at is 900
def refresh_sso_token() -> None:
    """Refresh the token every 6 minutes."""
    logger.debug("Getting session manager")
    session_manager = get_session_manager()
    logger.debug("Refreshing the token")
    session_manager.refresh_token()


@app.get("/cluster/{cluster_id}/upgrade-risks-prediction", response_model=UpgradeApiResponse)
async def upgrade_risks_prediction(cluster_id: UUID, settings: Settings = Depends(get_settings)):
    """Return the predition of an upgrade failure given a set of alerts and focs."""
    logger.info(f"Received cluster: {cluster_id}")

    logger.debug("Getting predictors from RHOBS")
    predictors = perform_rhobs_request(cluster_id)
    logger.debug("Getting inference result")
    inference_result = get_inference_for_predictors(predictors)
    logger.debug("Inference result is: ", inference_result)

    return inference_result
