"""Utils to interact with Inference service."""

import requests
from fastapi import HTTPException

from ccx_upgrades_data_eng.config import get_settings
from ccx_upgrades_data_eng.models import UpgradeApiResponse, UpgradeRisksPredictors


def get_inference_for_predictors(risk_predictors: UpgradeRisksPredictors) -> UpgradeApiResponse:
    """Request the inference service with a set of predictors."""
    settings = get_settings()

    inference_endpoint = f"{settings.inference_url}/upgrade-risks-prediction"
    inference_response = requests.get(inference_endpoint, data=risk_predictors.json())

    if inference_response.status_code != 200:
        raise HTTPException(status_code=inference_response.status_code)

    return UpgradeApiResponse.parse_obj(inference_response.json())
