"""Tests for the rhobs module."""

import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from ccx_upgrades_data_eng.rhobs import (
    alerts_and_focs,
    single_cluster_alerts_and_focs,
    perform_rhobs_request,
)
from ccx_upgrades_data_eng.tests import needed_env


RHOBS_EMPTY_REPONSE = {"status": "success", "data": {"resultType": "vector", "result": []}}
RHOBS_RESPONSE = {
    "status": "success",
    "data": {
        "resultType": "vector",
        "result": [
            # Console URL metric
            {
                "metric": {
                    "__name__": "console_url",
                    "_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "endpoint": "https",
                    "instance": "1.2.3.4:8443",
                    "job": "metrics",
                    "namespace": "openshift-console-operator",
                    "pod": "console-operator-6ff67b94c5-7k2mk",
                    "prometheus": "openshift-monitoring/k8s",
                    "receive": "true",
                    "service": "metrics",
                    "tenant_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "url": "https://console-openshift-console.some_url.com",
                },
                "value": [1677825120.237, "1"],
            },
            # Alert metric
            {
                "metric": {
                    "__name__": "alerts",
                    "_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "alertname": "APIRemovedInNextEUSReleaseInUse",
                    "alertstate": "firing",
                    "group": "batch",
                    "namespace": "openshift-kube-apiserver",
                    "prometheus": "openshift-monitoring/k8s",
                    "receive": "true",
                    "resource": "cronjobs",
                    "severity": "info",
                    "tenant_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "version": "v1beta1",
                },
                "value": [1677825120.237, "1"],
            },
            # FOC metric
            {
                "metric": {
                    "__name__": "cluster_operator_conditions",
                    "_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "condition": "Available",
                    "endpoint": "metrics",
                    "instance": "10.0.142.139:9099",
                    "job": "cluster-version-operator",
                    "name": "authentication",
                    "namespace": "openshift-cluster-version",
                    "pod": "cluster-version-operator-6b5c8ff5c8-vrmnl",
                    "prometheus": "openshift-monitoring/k8s",
                    "reason": "OAuthServerRouteEndpointAccessibleController_EndpointUnavailable",
                    "receive": "true",
                    "service": "cluster-version-operator",
                    "tenant_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                },
                "value": [1677825120.237, "0"],
            },
            # No metric key
            {
                "value": [1677825120.237, "0"],
            },
            # Unexpected metric
            {
                "metric": {
                    "__name__": "an unexpected metric name",
                },
                "value": [1677825120.237, "0"],
            },
        ],
    },
}


def test_single_cluster_alerts_and_focs():
    """Test if single_cluster_alerts_and_focs returns the expected query."""
    assert (
        single_cluster_alerts_and_focs("test")
        == """console_url{_id="test"}
or
alerts{_id="test", namespace=~"openshift-.*", severity=~"warning|critical"}
or
cluster_operator_conditions{_id="test", condition="Available"} == 0
or
cluster_operator_conditions{_id="test", condition="Degraded"} == 1"""
    )


def test_multi_cluster_alerts_and_focs():
    """Test if alerts_and_focs returns the expected query."""
    assert (
        alerts_and_focs(["test1", "test2"])
        == """console_url{_id="test1"}
or
alerts{_id="test1", namespace=~"openshift-.*", severity=~"warning|critical"}
or
cluster_operator_conditions{_id="test1", condition="Available"} == 0
or
cluster_operator_conditions{_id="test1", condition="Degraded"} == 1
or
console_url{_id="test2"}
or
alerts{_id="test2", namespace=~"openshift-.*", severity=~"warning|critical"}
or
cluster_operator_conditions{_id="test2", condition="Available"} == 0
or
cluster_operator_conditions{_id="test2", condition="Degraded"} == 1"""
    )


@pytest.mark.parametrize("response_status", [300, 404, 500])
@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request_not_ok(get_session_manager_mock, response_status):
    """Check result when RHOBS return a 404."""
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
def test_perform_rhobs_request_empty(get_session_manager_mock):
    """Check results when RHOBS sends OK but empty."""
    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = 200
    rhobs_response_mock.json.return_value = RHOBS_EMPTY_REPONSE

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"

    predictors, console_url = perform_rhobs_request(cluster_id)
    assert len(predictors.alerts) == 0
    assert len(predictors.operator_conditions) == 0
    assert console_url == ""


@patch.dict(os.environ, needed_env)
@patch("ccx_upgrades_data_eng.rhobs.get_session_manager")
def test_perform_rhobs_request(get_session_manager_mock):
    """Check results when RHOBS sends OK but empty."""
    # Prepare the mocks
    rhobs_response_mock = MagicMock()
    rhobs_response_mock.status_code = 200
    rhobs_response_mock.json.return_value = RHOBS_RESPONSE

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
    assert predictors.operator_conditions[0].condition == "Available"
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

    session_mock = MagicMock()
    session_mock.get.return_value = rhobs_response_mock

    session_manager_mock = MagicMock()
    session_manager_mock.get_session.return_value = session_mock

    get_session_manager_mock.return_value = session_manager_mock

    # Perform the request
    cluster_id = "34c3ecc5-624a-49a5-bab8-4fdc5e51a266"

    _, console_url = perform_rhobs_request(cluster_id)
    assert console_url == ""
