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
class TestMetricsEndpoint:  # pylint: disable=too-few-public-methods
    """Check the /metrics endpoint expose some metrics."""

    @mock.patch("ccx_upgrades_data_eng.main.get_session_manager")
    def test_http_requests_total(self, get_session_manager_mock):
        """Check that the http_requests_total metric exists."""
        with TestClient(app) as client:
            response = client.get("/metrics")
            assert get_session_manager_mock.called
            assert response.status_code == 200
            assert "http_requests_total" in response.text
