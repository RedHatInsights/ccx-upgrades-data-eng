"""Test main.py."""

import os
import json
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import UUID

from fastapi import HTTPException
from fastapi.testclient import TestClient

from ccx_upgrades_data_eng.main import app
from ccx_upgrades_data_eng.models import (
    UpgradeApiResponse,
    UpgradeRisksPredictors,
    UpgradeRisksPredictorsWithURLs,
)
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
        assert (
            response.json()["detail"][0]["msg"]
            == "Input should be a valid UUID, invalid character: expected an optional prefix of `urn:uuid:` followed by [0-9a-fA-F-], found `t` at 1"
        )

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
        test_date = datetime.now()

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
            upgrade_risks_predictors=UpgradeRisksPredictorsWithURLs.model_validate(
                risk_predictors.model_dump()
            ),
            last_checked_at=test_date,
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
        assert content["last_checked_at"] == test_date.isoformat()

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


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
def test_multi_cluster_endpoint_fails(get_session_manager_mock):
    """Test multi cluster endpoint fails with wrong HTTP request."""
    response = client.get("/upgrade-risks-prediction")
    assert response.status_code != 200

    response = client.put("/upgrade-risks-prediction")
    assert response.status_code != 200

    response = client.delete("/upgrade-risks-prediction")
    assert response.status_code != 200

    # Missing request body
    response = client.post("/upgrade-risks-prediction")
    assert response.status_code != 200


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
def test_multi_cluster_endpoint_no_clusters(get_session_manager_mock):
    """Test multi cluster endpoint success."""
    response = client.post(
        "/upgrade-risks-prediction",
        data=json.dumps({"clusters": []}),
        content="application/json",
    )
    assert response.status_code == 200


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.main.get_session_manager")
@patch("ccx_upgrades_data_eng.main.get_filled_inference_for_predictors")
@patch("ccx_upgrades_data_eng.main.perform_rhobs_request_multi_cluster")
def test_multi_cluster_endpoint_rhobs_ok_inference_ok(
    perform_rhobs_request_multi_cluster_mock,
    get_filled_inference_for_predictors_mock,
    get_session_manager_mock,
):
    """Test a request with valid data, when rhobs requests and inference works fine."""
    test_date = datetime.now()

    session_manager_mock = MagicMock()
    get_session_manager_mock.return_value = session_manager_mock

    risk_predictors = {"alerts": [], "operator_conditions": []}
    clusters_predictions = {
        UUID("34c3ecc5-624a-49a5-bab8-4fdc5e51a266"): (
            UpgradeRisksPredictors.model_validate(risk_predictors),
            "https://console_url.com",
        ),
        UUID("2b9195d4-85d4-428f-944b-4b46f08911f8"): (
            UpgradeRisksPredictors.model_validate(risk_predictors),
            "",
        ),
    }
    perform_rhobs_request_multi_cluster_mock.return_value = clusters_predictions
    get_filled_inference_for_predictors_mock.return_value = UpgradeApiResponse(
        upgrade_recommended=True,
        upgrade_risks_predictors=UpgradeRisksPredictorsWithURLs.model_validate(risk_predictors),
        last_checked_at=test_date,
    )

    response = client.post(
        "/upgrade-risks-prediction",
        data=json.dumps(
            {
                "clusters": [
                    "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "2b9195d4-85d4-428f-944b-4b46f08911f8",
                    "aae0ff10-9892-4572-b77f-73eb3e39825f",  # Cluster not in RHOBS
                ],
            }
        ),
    )
    content = response.json()

    expected_elements_in_result_array = [
        {
            "cluster_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
            "prediction_status": "ok",
            "upgrade_recommended": True,
            "upgrade_risks_predictors": {
                "alerts": [],
                "operator_conditions": [],
            },
            "last_checked_at": test_date.isoformat(),
        },
        {
            "cluster_id": "2b9195d4-85d4-428f-944b-4b46f08911f8",
            "prediction_status": "ok",
            "upgrade_recommended": True,
            "upgrade_risks_predictors": {
                "alerts": [],
                "operator_conditions": [],
            },
            "last_checked_at": test_date.isoformat(),
        },
        {
            "cluster_id": "aae0ff10-9892-4572-b77f-73eb3e39825f",
            "prediction_status": "No data for the cluster",
            "upgrade_recommended": None,
            "upgrade_risks_predictors": None,
            "last_checked_at": None,
        },
    ]

    assert perform_rhobs_request_multi_cluster_mock.called
    assert get_filled_inference_for_predictors_mock.call_count == 2
    assert response.status_code == 200
    assert len(content["predictions"]) == 3

    for expected_element_in_result in expected_elements_in_result_array:
        assert expected_element_in_result in content["predictions"]
