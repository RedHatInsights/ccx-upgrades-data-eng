"""Test the /metrics endpoint."""

import os
from unittest import mock

from fastapi.testclient import TestClient

from ccx_upgrades_data_eng.main import app

needed_env = {
    "CLIENT_ID": "client-id",
    "CLIENT_SECRET": "secret",
}


@mock.patch.dict(os.environ, needed_env)
@mock.patch("ccx_upgrades_data_eng.main.get_session_manager")
def test_metrics_are_populated(get_session_manager_mock):
    """Check that the metrics exist."""
    with TestClient(app) as client:
        response = client.get("/metrics")
        assert get_session_manager_mock.called
        assert response.status_code == 200
        assert "http_requests_total" in response.text
        assert "ccx_upgrades_prediction_total" in response.text
        assert "ccx_upgrades_risks_total" in response.text
        assert "ccx_upgrades_rhobs_time" in response.text
