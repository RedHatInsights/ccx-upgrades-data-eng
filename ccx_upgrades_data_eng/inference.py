"""Utils to interact with Inference service."""

import requests
from fastapi import HTTPException
import logging

from ccx_upgrades_data_eng.config import get_settings
from ccx_upgrades_data_eng.models import (
    UpgradeApiResponse,
    UpgradeRisksPredictors,
    InferenceResponse,
)


logger = logging.getLogger(__name__)


def get_inference_for_predictors(risk_predictors: UpgradeRisksPredictors) -> UpgradeApiResponse:
    """Request the inference service with a set of predictors."""
    settings = get_settings()

    inference_endpoint = f"{settings.inference_url}/upgrade-risks-prediction"
    inference_response = requests.get(inference_endpoint, data=risk_predictors.json(), timeout=5)

    if inference_response.status_code != 200:
        raise HTTPException(status_code=inference_response.status_code)

    logger.debug("Inference response status code: %s", inference_response.status_code)
    logger.debug("Inference response text: %s", inference_response.text)

    inference_response = InferenceResponse.parse_obj(inference_response.json())
    risks = inference_response.upgrade_risks_predictors

    return UpgradeApiResponse(
        upgrade_recommended=calculate_upgrade_recommended(risks), upgrade_risks_predictors=risks
    )


def calculate_upgrade_recommended(risks: UpgradeRisksPredictors) -> bool:
    """If there are more than 0 risks predictors, return False."""
    return len(risks.alerts + risks.operator_conditions) == 0
