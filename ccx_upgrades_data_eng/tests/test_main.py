"""Test main.py."""

import os
from unittest import mock
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from ccx_upgrades_data_eng.main import (
    app,
    get_session_manager,
    init_session_manager,
)
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
    def test_valid_parameter(self, get_session_manager_mock):
        """If the request has a valid cluster_id it should work."""
        params = {"cluster_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"}
        response = client.get("/upgrade-risks-prediction", params=params)
        assert get_session_manager_mock.called
        assert response.status_code == 200
        assert not response.json()["upgrade_recommended"]
        assert response.json()["upgrade_risks_predictors"] == EXAMPLE_PREDICTORS

    @patch("ccx_upgrades_data_eng.main.get_session_manager")
    def test_valid_parameter_no_rhobs_data(self, get_session_manager_mock):
        """If the request has a valid cluster_id it should work."""
        # Prepare the mocks
        session_manager_mock = MagicMock()
        session_mock = MagicMock()
        response_mock = MagicMock()

        response_mock.status_code = 404

        get_session_manager_mock.return_value = session_manager_mock
        session_manager_mock.get_session.return_value = session_mock
        session_mock.get.return_value = response_mock

        params = {"cluster_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"}
        response = client.get("/upgrade-risks-prediction", params=params)

        assert get_session_manager_mock.called

        assert response.status_code == 404


def test_get_session_manager_cache():
    """Check that get_session_manager always return the same instance."""
    first_instance = get_session_manager()
    second_instance = get_session_manager()

    assert first_instance is second_instance


@patch("ccx_upgrades_data_eng.main.get_session_manager")
def test_init_session_manager(get_session_manager_mock):
    """Check that init_session_manager tries to get the session and refresh the token."""
    session_manager_mock = MagicMock()
    get_session_manager_mock.return_value = session_manager_mock

    init_session_manager()

    assert get_session_manager_mock.called
    assert session_manager_mock.refresh_token.called
