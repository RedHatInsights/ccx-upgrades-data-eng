"""Test main.py."""

import os
from unittest import mock
from unittest.mock import patch

from fastapi.testclient import TestClient

from ccx_upgrades_data_eng.main import app
from ccx_upgrades_data_eng.examples import EXAMPLE_PREDICTORS


client = TestClient(app)
needed_env = {
    "CLIENT_ID": "client-id",
    "CLIENT_SECRET": "secret",
}


@mock.patch.dict(os.environ, needed_env)
class TestUpgradeRisksPrediction:  # pylint: disable=too-few-public-methods
    """Check the /upgrade-risks-prediction endpoint."""

    def test_no_parameter(self):
        """If the request has no parameters it should return a 422."""
        response = client.get("/upgrade-risks-prediction")
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "field required"

    def test_unexpected_parameter(self):
        """If the request has an unexpected parameter it should return a 422."""
        params = {"cluster_id": "test"}
        response = client.get("/upgrade-risks-prediction", params=params)
        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "value is not a valid uuid"

    @patch("ccx_upgrades_data_eng.main.get_session_manager")
    def test_valid_parameter(self, session_mock):
        """If the request has a valid cluster_id it should work."""
        params = {"cluster_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"}
        response = client.get("/upgrade-risks-prediction", params=params)
        assert session_mock.called
        assert response.status_code == 200
        assert not response.json()["upgrade_recommended"]
        assert response.json()["upgrade_risks_predictors"] == EXAMPLE_PREDICTORS
