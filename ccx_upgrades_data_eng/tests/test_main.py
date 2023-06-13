"""Test main.py."""

import os
from unittest.mock import MagicMock, patch
import pytest

from fastapi import HTTPException, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from ccx_upgrades_data_eng.main import (
    app,
    refresh_sso_token,
)
from ccx_upgrades_data_eng.auth import SessionManagerException, TokenException
from ccx_upgrades_data_eng.models import UpgradeApiResponse, UpgradeRisksPredictors
from ccx_upgrades_data_eng.tests import needed_env

client = TestClient(app)


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
class TestUpgradeRisksPrediction:  # pylint: disable=too-few-public-methods
    """Check the /upgrade-risks-prediction endpoint."""

    def test_old_endpoint(self, get_session_manager_mock):
        """Test old endpoint should return a 404."""
        session_manager_mock = MagicMock()
        get_session_manager_mock.return_value = session_manager_mock

        cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
        response = client.get(f"/upgrade-risks-prediction/{cluster_id}")

        assert response.status_code == 404

    def test_unexpected_parameter(self, get_session_manager_mock):
        """If the request has an unexpected parameter it should return a 422."""
        session_manager_mock = MagicMock()
        get_session_manager_mock.return_value = session_manager_mock

        response = client.get("/cluster/test/upgrade-risks-prediction")
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "value is not a valid uuid"

    @patch("ccx_upgrades_data_eng.main.perform_rhobs_request")
    def test_valid_parameter_rhobs_error(
        self, perform_rhobs_request_mock, get_session_manager_mock
    ):
        """If the request has a valid cluster_id it should work."""
        # Prepare the mocks
        session_manager_mock = MagicMock()
        get_session_manager_mock.return_value = session_manager_mock
        perform_rhobs_request_mock.side_effect = HTTPException(status_code=404)

        cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
        response = client.get(f"/cluster/{cluster_id}/upgrade-risks-prediction")

        assert perform_rhobs_request_mock.called
        assert response.status_code == 404

    @patch("ccx_upgrades_data_eng.main.get_filled_inference_for_predictors")
    @patch("ccx_upgrades_data_eng.main.perform_rhobs_request")
    def test_valid_parameter_rhobs_ok_inference_nok(
        self,
        perform_rhobs_request_mock,
        get_filled_inference_for_predictors_mock,
        get_session_manager_mock,
    ):
        """If the request has a valid cluster_id it should work."""
        # Prepare the mocks
        session_manager_mock = MagicMock()
        get_session_manager_mock.return_value = session_manager_mock
        perform_rhobs_request_mock.return_value = UpgradeRisksPredictors(
            alerts=[],
            operator_conditions=[],
        )

        get_filled_inference_for_predictors_mock.side_effect = HTTPException(500)

        cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
        response = client.get(f"/cluster/{cluster_id}/upgrade-risks-prediction")

        assert perform_rhobs_request_mock.called
        assert get_filled_inference_for_predictors_mock.called
        assert response.status_code == 500

    @patch("ccx_upgrades_data_eng.main.get_filled_inference_for_predictors")
    @patch("ccx_upgrades_data_eng.main.perform_rhobs_request")
    def test_valid_parameter_rhobs_ok_inference_ok(
        self,
        perform_rhobs_request_mock,
        get_filled_inference_for_predictors_mock,
        get_session_manager_mock,
    ):
        """If the request has a valid cluster_id it should work."""
        session_manager_mock = MagicMock()
        get_session_manager_mock.return_value = session_manager_mock
        risk_predictors = UpgradeRisksPredictors(
            alerts=[],
            operator_conditions=[],
        )

        # Prepare the mocks
        perform_rhobs_request_mock.return_value = (
            risk_predictors,
            "https://console_url.com",
        )
        get_filled_inference_for_predictors_mock.return_value = UpgradeApiResponse(
            upgrade_recommended=True,
            upgrade_risks_predictors=risk_predictors,
        )

        cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
        response = client.get(f"/cluster/{cluster_id}/upgrade-risks-prediction")
        content = response.json()

        assert perform_rhobs_request_mock.called
        assert get_filled_inference_for_predictors_mock.called
        assert response.status_code == 200
        assert content["upgrade_recommended"]
        assert content["upgrade_risks_predictors"] == {
            "alerts": [],
            "operator_conditions": [],
        }

    @patch("ccx_upgrades_data_eng.main.get_filled_inference_for_predictors")
    @patch("ccx_upgrades_data_eng.main.perform_rhobs_request")
    def test_valid_parameter_rhobs_no_cluster_version(
        self,
        perform_rhobs_request_mock,
        get_filled_inference_for_predictors_mock,
        get_session_manager_mock,
    ):
        """If the request has a valid cluster_id it should work."""
        session_manager_mock = MagicMock()
        get_session_manager_mock.return_value = session_manager_mock
        risk_predictors = UpgradeRisksPredictors(
            alerts=[],
            operator_conditions=[],
        )

        # Prepare the mocks
        perform_rhobs_request_mock.return_value = (
            risk_predictors,
            "",
        )  # return an empty cluster_url

        cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
        response = client.get(f"/cluster/{cluster_id}/upgrade-risks-prediction")

        assert perform_rhobs_request_mock.called
        assert not get_filled_inference_for_predictors_mock.called
        assert response.status_code == 404
        assert "No data" in response.text


async def mock_call_next(request: Request):
    """Mock the call_next function in the refresh_sso_token middleware."""
    return JSONResponse("test", status_code=200)


@pytest.mark.asyncio
@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
async def test_refresh_sso_token_session_ok(get_session_manager_mock):
    """Check that refresh_sso_token tries to get the session and refresh the token."""
    session_manager_mock = MagicMock()
    get_session_manager_mock.return_value = session_manager_mock

    resp = await refresh_sso_token(Request({"type": "http"}), mock_call_next)

    assert get_session_manager_mock.called
    assert session_manager_mock.refresh_token.called

    assert resp.status_code == 200


@pytest.mark.asyncio
@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
async def test_refresh_sso_token_session_manager_exception(get_session_manager_mock):
    """Check that refresh_sso_token tries to get the session and refresh the token."""
    session_manager_mock = MagicMock()
    get_session_manager_mock.side_effect = SessionManagerException("test")
    get_session_manager_mock.return_value = session_manager_mock

    resp = await refresh_sso_token(Request({"type": "http"}), mock_call_next)

    assert get_session_manager_mock.called
    assert not session_manager_mock.refresh_token.called

    assert resp.status_code == 503


@pytest.mark.asyncio
@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
async def test_refresh_sso_token_token_exception(get_session_manager_mock):
    """Check that refresh_sso_token tries to get the session and refresh the token."""
    session_manager_mock = MagicMock()
    session_manager_mock.refresh_token.side_effect = TokenException("test")
    get_session_manager_mock.return_value = session_manager_mock

    resp = await refresh_sso_token(Request({"type": "http"}), mock_call_next)

    assert get_session_manager_mock.called
    assert session_manager_mock.refresh_token.called

    assert resp.status_code == 503
