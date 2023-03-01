"""Definition of the REST API for the inference service."""

import logging
from functools import lru_cache
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from fastapi_utils.tasks import repeat_every

from ccx_upgrades_data_eng.auth import Oauth2Manager
from ccx_upgrades_data_eng.config import get_settings, Settings
from ccx_upgrades_data_eng.examples import EXAMPLE_PREDICTORS
from ccx_upgrades_data_eng.models import UpgradeApiResponse
from ccx_upgrades_data_eng.rhobs_queries import single_cluster_alerts_and_focs

from prometheus_fastapi_instrumentator import Instrumentator

logger = logging.getLogger(__name__)
app = FastAPI()


@app.on_event("startup")
async def expose_metrics():
    """Expose the prometheus metrics in the /metrics endpoint."""
    logger.info("Metrics available at /metrics")
    Instrumentator().instrument(app).expose(app)


@lru_cache()
def get_session_manager() -> Oauth2Manager:
    """Oauth2Manager cache."""
    settings = get_settings()
    return Oauth2Manager(
        settings.client_id,
        settings.client_secret,
        settings.sso_issuer,
    )


@app.on_event("startup")
def init_session_manager() -> None:
    """Force Oauth2Manager to refresh its token periodically."""
    session_manager = get_session_manager()
    session_manager.refresh_token()


@app.on_event("startup")
@repeat_every(seconds=360)  # repeat every 6 minutes, default expires_at is 900
def refresh_sso_token() -> None:
    """Refresh the token every 6 minutes."""
    session_manager = get_session_manager()
    session_manager.refresh_token()


@app.get("/cluster/{cluster_id}/upgrade-risks-prediction", response_model=UpgradeApiResponse)
async def upgrade_risks_prediction(cluster_id: UUID, settings: Settings = Depends(get_settings)):
    """Return the predition of an upgrade failure given a set of alerts and focs."""
    logger.info(f"Received cluster: {cluster_id}")
    query = single_cluster_alerts_and_focs(cluster_id)

    rhobs_endpoint = f"/api/metrics/v1/{settings.rhobs_tenant}/api/v1/query"
    session = get_session_manager().get_session()

    response = session.get(
        f"{settings.rhobs_url}{rhobs_endpoint}",
        params={"query": query},
        timeout=settings.rhobs_request_timeout,
    )

    content = response.json()
    logger.info(
        "Observatorium response contains %s results",
        len(content["data"]["result"]),
    )
    logger.debug("Observatorium request elapsed time: %s", response.elapsed.total_seconds())
    logger.debug("Observatorium response results: %s", content)

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # TODO: CCXDEV-10301 wait until dictionary based on Alert and OperatorCondition is delivered
    # inference_endpoint = f"{settings.inference_url}/upgrade-risks-prediction"
    # requests.get(inference_endpoint, params={})

    return UpgradeApiResponse(
        upgrade_recommended=False, upgrade_risks_predictors=EXAMPLE_PREDICTORS
    )
