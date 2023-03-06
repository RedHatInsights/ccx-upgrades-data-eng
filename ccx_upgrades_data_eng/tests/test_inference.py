"""Tests for the inference module."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from ccx_upgrades_data_eng.inference import get_inference_for_predictors
from ccx_upgrades_data_eng.examples import EXAMPLE_PREDICTORS
from ccx_upgrades_data_eng.models import UpgradeRisksPredictors
from ccx_upgrades_data_eng.tests import needed_env


INFERENCE_UPGRADE_MOCKED_RESPONSE = {
    "upgrade_recommended": True,
    "upgrade_risks_predictors": {
        "alerts": [],
        "operator_conditions": [],
    },
}

INFERENCE_DONT_UPGRADE_MOCKED_RESPONSE = {
    "upgrade_recommended": False,
    "upgrade_risks_predictors": EXAMPLE_PREDICTORS,
}


@patch.dict(os.environ, needed_env)
@patch("requests.get")
def test_get_inference_for_predictors_inference_not_ok(get_mock):
    """Check response when inference service returns not OK response."""
    response_mock = MagicMock()
    response_mock.status_code = 404
    get_mock.return_value = response_mock

    risk_predictors = UpgradeRisksPredictors(
        alerts=[],
        operator_conditions=[],
    )
    with pytest.raises(HTTPException):
        get_inference_for_predictors(risk_predictors)


@patch.dict(os.environ, needed_env)
@patch("requests.get")
def test_get_inference_for_predictors_inference_ok_empty(get_mock):
    """Check response when inference service returns not OK response."""
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = INFERENCE_UPGRADE_MOCKED_RESPONSE
    get_mock.return_value = response_mock

    risk_predictors = UpgradeRisksPredictors(
        alerts=[],
        operator_conditions=[],
    )
    response = get_inference_for_predictors(risk_predictors)
    assert response.upgrade_recommended
    # With an empty risk prediction, the response should be always the same
    assert response.upgrade_risks_predictors == risk_predictors


@patch.dict(os.environ, needed_env)
@patch("requests.get")
def test_get_inference_for_predictors_inference_ok(get_mock):
    """Check response when inference service returns not OK response."""
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = INFERENCE_DONT_UPGRADE_MOCKED_RESPONSE
    get_mock.return_value = response_mock

    risk_predictors = UpgradeRisksPredictors(
        alerts=[],
        operator_conditions=[],
    )
    response = get_inference_for_predictors(risk_predictors)
    assert not response.upgrade_recommended
    # With an empty risk prediction, the response should be always the same
    assert response.upgrade_risks_predictors == EXAMPLE_PREDICTORS
