"""Tests for the inference module."""

import os
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
import pytest
from fastapi import HTTPException

from ccx_upgrades_data_eng.inference import (
    get_inference_for_predictors,
    get_filled_inference_for_predictors,
    calculate_upgrade_recommended,
)
from ccx_upgrades_data_eng.examples import (
    EXAMPLE_CONSOLE_URL,
    EXAMPLE_PREDICTORS,
    EXAMPLE_PREDICTORS_WITH_EMPTY_URL,
    EXAMPLE_PREDICTORS_WITH_URL,
)
from ccx_upgrades_data_eng.models import UpgradeRisksPredictors, FOC
from ccx_upgrades_data_eng.tests import needed_env

INFERENCE_UPGRADE_MOCKED_RESPONSE_EMPTY_PREDICTORS = {
    "upgrade_risks_predictors": {
        "alerts": [],
        "operator_conditions": [],
    },
}

INFERENCE_UPGRADE_MOCKED_RESPONSE_WITH_PREDICTORS = {
    "upgrade_risks_predictors": EXAMPLE_PREDICTORS,
}

INFERENCE_UPGRADE_MOCKED_RESPONSE_WITH_FILLED_URLS = {
    "upgrade_risks_predictors": EXAMPLE_PREDICTORS_WITH_URL,
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
    """Check response when inference service returns no predictors."""
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = INFERENCE_UPGRADE_MOCKED_RESPONSE_EMPTY_PREDICTORS
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
def test_get_inference_for_predictors_inference_ok_full(get_mock):
    """Check response when inference service returns more than 0 predictors."""
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = INFERENCE_UPGRADE_MOCKED_RESPONSE_WITH_PREDICTORS
    get_mock.return_value = response_mock

    risk_predictors = UpgradeRisksPredictors.parse_obj(EXAMPLE_PREDICTORS)
    response = get_inference_for_predictors(risk_predictors)
    assert not response.upgrade_recommended
    # With an empty risk prediction, the response should be always the same
    assert response.upgrade_risks_predictors == EXAMPLE_PREDICTORS_WITH_EMPTY_URL


def test_calculate_upgrade_recommended_0_predictors():
    """Check the upgrade is recommended if 0 predictors."""
    risk_predictors = UpgradeRisksPredictors(
        alerts=[],
        operator_conditions=[],
    )
    assert calculate_upgrade_recommended(risk_predictors)


def test_calculate_upgrade_recommended_1_predictor():
    """Check the upgrade is recommended if > 0 predictors."""
    risk_predictors = UpgradeRisksPredictors(
        alerts=[],
        operator_conditions=[FOC(name="test", condition="test")],
    )
    assert not calculate_upgrade_recommended(risk_predictors)


@patch.dict(os.environ, needed_env)
@patch("requests.get")
def test_get_filled_inference_for_predictors_ok(get_mock):
    """Check response when inference service returns more than 0 predictors."""
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = INFERENCE_UPGRADE_MOCKED_RESPONSE_WITH_FILLED_URLS
    get_mock.return_value = response_mock

    risk_predictors = UpgradeRisksPredictors.parse_obj(EXAMPLE_PREDICTORS)
    response = get_filled_inference_for_predictors(risk_predictors, EXAMPLE_CONSOLE_URL)
    assert not response.upgrade_recommended
    # With an empty risk prediction, the response should be always the same
    assert response.upgrade_risks_predictors == EXAMPLE_PREDICTORS_WITH_URL


@patch.dict(os.environ, needed_env)
@patch("requests.get")
def test_last_checked_at(get_mock):
    """Check the last_checked_at field is updated correctly."""
    response_mock = MagicMock()
    response_mock.status_code = 200
    response_mock.json.return_value = INFERENCE_UPGRADE_MOCKED_RESPONSE_WITH_FILLED_URLS
    get_mock.return_value = response_mock

    risk_predictors = UpgradeRisksPredictors.parse_obj(EXAMPLE_PREDICTORS)
    response = get_inference_for_predictors(risk_predictors)
    assert (
        datetime.now(tz=timezone.utc) - timedelta(minutes=1)
        < response.last_checked_at
        < datetime.now(tz=timezone.utc)
    )
