"""Tests for the rhobs module."""

import importlib
import os
import sys
from requests.exceptions import ConnectionError
from unittest.mock import MagicMock, patch
from uuid import UUID

import pytest
from fastapi import HTTPException

from ccx_upgrades_data_eng.rhobs import (
    alerts_and_focs,
    perform_rhobs_request,
    perform_rhobs_request_multi_cluster,
    update_cache_for_cluster,
)
from ccx_upgrades_data_eng.models import UpgradeRisksPredictors
from ccx_upgrades_data_eng.utils import LoggedTTLCache

from ccx_upgrades_data_eng.tests import (
    needed_env,
    needed_env_cache_enabled,
    RHOBS_EMPTY_REPONSE,
    RHOBS_RESPONSE,
    RHOBS_RESPONSE_MULTI_CLUSTER,
    RHOBS_RESPONSE_NONE_RESULT,
)


def test_alerts_and_focs():
    """Test if alerts_and_focs returns the expected query."""
    assert alerts_and_focs(["test1", "test2"]) == """console_url{_id=~"test1|test2"}
or
alerts{_id=~"test1|test2", namespace=~"openshift-.*", severity=~"warning|critical"}
or
cluster_operator_conditions{_id=~"test1|test2", condition="Available"} == 0
or
cluster_operator_conditions{_id=~"test1|test2", condition="Degraded"} == 1"""


@pytest.mark.parametrize("response_status", [300, 404, 500])
@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request_not_ok(get_session_manager_mock, response_status):
    """Check result when RHOBS return a non 200."""
    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = response_status

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"

    with pytest.raises(HTTPException):
        perform_rhobs_request(cluster_id)


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request_connection_error(get_session_manager_mock):
    """Check result when RHOBS return a non 200."""
    # Prepare the mocks
    session_mock = MagicMock()
    session_mock.get.side_effect = ConnectionError("Mock failure")

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"

    with pytest.raises(HTTPException):
        perform_rhobs_request(cluster_id)


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request_empty(get_session_manager_mock):
    """Check results when RHOBS sends OK but empty."""
    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = 200
    rhobs_response_mock.json.return_value = RHOBS_EMPTY_REPONSE
    rhobs_response_mock.elapsed.total_seconds.return_value = 1

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"

    predictors, console_url = perform_rhobs_request(cluster_id)
    assert predictors is None
    assert console_url is None


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request(get_session_manager_mock):
    """Check results when RHOBS sends OK but empty."""
    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = 200
    rhobs_response_mock.json.return_value = RHOBS_RESPONSE
    rhobs_response_mock.elapsed.total_seconds.return_value = 1

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"

    predictors, console_url = perform_rhobs_request(cluster_id)
    assert len(predictors.alerts) == 1
    assert len(predictors.operator_conditions) == 1
    assert predictors.alerts[0].name == "APIRemovedInNextEUSReleaseInUse"
    assert predictors.alerts[0].namespace == "openshift-kube-apiserver"
    assert predictors.alerts[0].severity == "info"
    assert predictors.operator_conditions[0].name == "authentication"
    assert predictors.operator_conditions[0].condition == "Not Available"
    assert (
        predictors.operator_conditions[0].reason
        == "OAuthServerRouteEndpointAccessibleController_EndpointUnavailable"
    )
    assert console_url == "https://console-openshift-console.some_url.com"


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request_no_cluster_version(get_session_manager_mock):
    """Check result when RHOBS doesn't contain any cluster version."""
    rhobs_response = RHOBS_RESPONSE.copy()
    # delete the url from the metric content
    del rhobs_response["data"]["result"][0]["metric"]["url"]

    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = 200
    rhobs_response_mock.json.return_value = rhobs_response
    rhobs_response_mock.elapsed.total_seconds.return_value = 1

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"

    _, console_url = perform_rhobs_request(cluster_id)
    assert console_url == ""


@pytest.mark.parametrize("response_status", [300, 404, 500])
@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request_multi_cluster_nok(get_session_manager_mock, response_status):
    """Check result when RHOBS return a non 200."""
    # repare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = response_status

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
    result = perform_rhobs_request_multi_cluster([cluster_id])
    assert result == dict()


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request_multi_cluster_all_cached(get_session_manager_mock):
    """Check result when all results are cached."""
    # prepare mocks
    session_mock = MagicMock()

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
    predictors = UpgradeRisksPredictors(alerts=[], operator_conditions=[])

    # Re-create perform_rhobs_request cache to use enabled TTLCache
    old_cache = perform_rhobs_request.cache
    perform_rhobs_request.cache = LoggedTTLCache(maxsize=1, ttl=10)
    perform_rhobs_request.cache[(cluster_id,)] = predictors, "console_url"

    result = perform_rhobs_request_multi_cluster([cluster_id])
    assert not session_mock.get.called
    assert cluster_id in result

    perform_rhobs_request.cache = old_cache


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request_multi_cluster_empty(get_session_manager_mock):
    """Check results when RHOBS sends OK but empty."""
    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = 200
    rhobs_response_mock.json.return_value = RHOBS_EMPTY_REPONSE
    rhobs_response_mock.elapsed.total_seconds.return_value = 1

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"

    result = perform_rhobs_request_multi_cluster([cluster_id])
    assert cluster_id not in result


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request_multi_cluster(get_session_manager_mock):
    """Check results when RHOBS sends OK but empty."""
    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = 200
    rhobs_response_mock.json.return_value = RHOBS_RESPONSE_MULTI_CLUSTER
    rhobs_response_mock.elapsed.total_seconds.return_value = 1

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    uuid_ok = UUID("34c3ecc5-624a-49a5-bab8-4fdc5e51a266")
    uuid_missing = UUID("2b9195d4-85d4-428f-944b-4b46f08911f8")

    # Perform the request
    clusters = [
        uuid_ok,
        uuid_missing,
    ]

    cluster_predictions = perform_rhobs_request_multi_cluster(clusters)

    assert len(cluster_predictions) == 2
    assert len(cluster_predictions[uuid_ok][0].alerts) == 1
    assert len(cluster_predictions[uuid_ok][0].operator_conditions) == 1
    assert cluster_predictions[uuid_ok][0].alerts[0].name == "APIRemovedInNextEUSReleaseInUse"
    assert cluster_predictions[uuid_ok][0].alerts[0].namespace == "openshift-kube-apiserver"
    assert cluster_predictions[uuid_ok][0].alerts[0].severity == "info"
    assert cluster_predictions[uuid_ok][0].operator_conditions[0].name == "authentication"
    assert cluster_predictions[uuid_ok][0].operator_conditions[0].condition == "Not Available"
    assert (
        cluster_predictions[uuid_ok][0].operator_conditions[0].reason
        == "OAuthServerRouteEndpointAccessibleController_EndpointUnavailable"
    )
    assert cluster_predictions[uuid_ok][1] == "https://console-openshift-console.some_url.com"


def test_update_cache_for_cluster():
    """Check if the RHOBS cache is updated properly."""
    cluster_id = "dc549b77-1913-46b2-8be6-088b54fb4da6"
    expected_predictors = UpgradeRisksPredictors(alerts=[], operator_conditions=[])
    expected_console_url = "https://the-console-url.com"

    old_cache = perform_rhobs_request.cache
    perform_rhobs_request.cache = LoggedTTLCache(maxsize=1, ttl=1000000)

    # Update the cache
    update_cache_for_cluster(cluster_id, (expected_predictors, expected_console_url))

    predictors, console_url = perform_rhobs_request.cache.get((cluster_id,))
    perform_rhobs_request.cache = old_cache

    assert predictors == expected_predictors
    assert console_url == expected_console_url


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_rhobs_result_none(get_session_manager_mock):
    """Check results when RHOBS sends ok with None result."""
    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = 200
    rhobs_response_mock.json.return_value = RHOBS_RESPONSE_NONE_RESULT
    rhobs_response_mock.elapsed.total_seconds.return_value = 1

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    uuid_ok = UUID("34c3ecc5-624a-49a5-bab8-4fdc5e51a266")
    uuid_missing = UUID("2b9195d4-85d4-428f-944b-4b46f08911f8")

    # Perform the request
    clusters = [
        uuid_ok,
        uuid_missing,
    ]

    cluster_predictions = perform_rhobs_request_multi_cluster(clusters)

    assert len(cluster_predictions) == 0


@patch.dict(os.environ, needed_env_cache_enabled)
@patch("ccx_upgrades_data_eng.auth.get_session_manager")
def test_perform_rhobs_request_multi_cluster_after_single_cluster_empty(get_session_manager_mock):
    """Check RHOBS multi cluster response after cached no data single cluster response."""
    # RHOBS functions need to be reloaded because cache
    # has to be initialized with correct env variables
    importlib.reload(sys.modules["ccx_upgrades_data_eng.rhobs"])
    from ccx_upgrades_data_eng.rhobs import (
        perform_rhobs_request,
        perform_rhobs_request_multi_cluster,
    )

    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = 200
    rhobs_response_mock.json.return_value = RHOBS_EMPTY_REPONSE
    rhobs_response_mock.elapsed.total_seconds.return_value = 1

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the single cluster RHOBS request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"
    predictions, console_url = perform_rhobs_request(cluster_id)
    assert predictions is None
    assert console_url is None

    # Check the cache contains expected values
    cached_result = perform_rhobs_request.cache.get((cluster_id,))
    assert cached_result is not None

    cached_predictions, cached_console_url = cached_result
    assert cached_predictions is None
    assert cached_console_url is None

    # Perform the multi cluster RHOBS request using cached result
    result = perform_rhobs_request_multi_cluster([cluster_id])
    assert cluster_id not in result
