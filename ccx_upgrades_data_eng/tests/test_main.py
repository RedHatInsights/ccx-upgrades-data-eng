"""Test main.py."""

import os
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from ccx_upgrades_data_eng.main import (
    app,
    init_session_manager,
)
from ccx_upgrades_data_eng.models import UpgradeApiResponse, UpgradeRisksPredictors
from ccx_upgrades_data_eng.tests import needed_env


client = TestClient(app)


@patch.dict(os.environ, needed_env)
class TestUpgradeRisksPrediction:  # pylint: disable=too-few-public-methods
    """Check the /upgrade-risks-prediction endpoint."""

    def test_old_endpoint(self):
        """Test old endpoint should return a 404."""
        cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
        response = client.get(f"/upgrade-risks-prediction/{cluster_id}")

        assert response.status_code == 404

    def test_unexpected_parameter(self):
        """If the request has an unexpected parameter it should return a 422."""
        response = client.get("/cluster/test/upgrade-risks-prediction")
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "value is not a valid uuid"

    @patch("ccx_upgrades_data_eng.main.perform_rhobs_request")
    def test_valid_parameter_rhobs_error(self, perform_rhobs_request_mock):
        """If the request has a valid cluster_id it should work."""
        # Prepare the mocks
        perform_rhobs_request_mock.side_effect = HTTPException(status_code=404)

        cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
        response = client.get(f"/cluster/{cluster_id}/upgrade-risks-prediction")

        assert perform_rhobs_request_mock.called
        assert response.status_code == 404

    @patch("ccx_upgrades_data_eng.main.get_inference_for_predictors")
    @patch("ccx_upgrades_data_eng.main.perform_rhobs_request")
    def test_valid_parameter_rhobs_ok_inference_nok(
        self, perform_rhobs_request_mock, get_inference_for_predictors_mock
    ):
        """If the request has a valid cluster_id it should work."""
        # Prepare the mocks
        perform_rhobs_request_mock.return_value = UpgradeRisksPredictors(
            alerts=[],
            operator_conditions=[],
        )

        get_inference_for_predictors_mock.side_effect = HTTPException(500)

        cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
        response = client.get(f"/cluster/{cluster_id}/upgrade-risks-prediction")

        assert perform_rhobs_request_mock.called
        assert get_inference_for_predictors_mock.called
        assert response.status_code == 500

    @patch("ccx_upgrades_data_eng.main.get_inference_for_predictors")
    @patch("ccx_upgrades_data_eng.main.perform_rhobs_request")
    def test_valid_parameter_rhobs_ok_inference_ok(
        self, perform_rhobs_request_mock, get_inference_for_predictors_mock
    ):
        """If the request has a valid cluster_id it should work."""
        risk_predictors = UpgradeRisksPredictors(
            alerts=[],
            operator_conditions=[],
        )

        # Prepare the mocks
        perform_rhobs_request_mock.return_value = risk_predictors
        get_inference_for_predictors_mock.return_value = UpgradeApiResponse(
            upgrade_recommended=True,
            upgrade_risks_predictors=risk_predictors,
        )

        cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
        response = client.get(f"/cluster/{cluster_id}/upgrade-risks-prediction")
        content = response.json()

        assert perform_rhobs_request_mock.called
        assert get_inference_for_predictors_mock.called
        assert response.status_code == 200
        assert content["upgrade_recommended"]
        assert content["upgrade_risks_predictors"] == {
            "alerts": [],
            "operator_conditions": [],
        }


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
def test_init_session_manager(get_session_manager_mock):
    """Check that init_session_manager tries to get the session and refresh the token."""
    session_manager_mock = MagicMock()
    get_session_manager_mock.return_value = session_manager_mock

    init_session_manager()

    assert get_session_manager_mock.called
    assert session_manager_mock.refresh_token.called
