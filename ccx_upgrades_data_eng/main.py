"""Definition of the REST API for the inference service."""

from fastapi import FastAPI
from uuid import UUID

from ccx_upgrades_data_eng.models import UpgradeApiResponse
from ccx_upgrades_data_eng.examples import EXAMPLE_PREDICTORS


app = FastAPI()


@app.get("/upgrade-risks-prediction/", response_model=UpgradeApiResponse)
async def upgrade_risks_prediction(cluster_id: UUID):
    """Return the predition of an upgrade failure given a set of alerts and focs."""
    # TODO @jdiazsua (CCXDEV-9850): Query the real RHOBS
    # TODO @jdiazsua (CCXDEV-9855): Use the real inference service
    print(cluster_id)
    return UpgradeApiResponse(
        upgrade_recommended=False, upgrade_risks_predictors=EXAMPLE_PREDICTORS
    )
