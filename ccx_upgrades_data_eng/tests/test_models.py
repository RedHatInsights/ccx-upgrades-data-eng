"""Test models.py."""

import pydantic
import pytest

from ccx_upgrades_data_eng.models import Alert, FOC, UpgradeApiResponse, InferenceResponse
from ccx_upgrades_data_eng.examples import EXAMPLE_PREDICTORS


GOOD_ALERTS = [
    {
        "metric": {
            "__name__": "alerts",
            "_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
            "alertname": "APIRemovedInNextEUSReleaseInUse",
            "alertstate": "firing",
            "group": "batch",
            "namespace": "openshift-kube-apiserver",
            "prometheus": "openshift-monitoring/k8s",
            "receive": "true",
            "resource": "cronjobs",
            "severity": "info",
            "tenant_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
            "version": "v1beta1",
        },
        "value": [
            1677825120.237,
            "1",
        ],
    },
    {
        "metric": {
            "__name__": "alerts",
            "_id": "050103b0-3ea9-4e58-8722-05b878ba54d5",
            "alertname": "APIRemovedInNextEUSReleaseInUse",
            "alertstate": "firing",
            "group": "policy",
            "prometheus": "openshift-monitoring/k8s",
            "receive": "true",
            "resource": "poddisruptionbudgets",
            "severity": "info",
            "tenant_id": "FB870BF3-9F3A-44FF-9BF7-D7A047A52F43",
            "version": "v1beta1",
        },
        "value": [1677825120.237, "1"],
    },
]

BAD_ALERTS = [
    {
        "metric": {
            "__name__": "alerts",
            "_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
            "alertstate": "firing",
            "group": "batch",
            "namespace": "openshift-kube-apiserver",
            "prometheus": "openshift-monitoring/k8s",
            "receive": "true",
            "resource": "cronjobs",
            "severity": "info",
            "tenant_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
            "version": "v1beta1",
        },
        "value": [
            1677825120.237,
            "1",
        ],
    },
    {
        "metric": {
            "__name__": "alerts",
            "_id": "050103b0-3ea9-4e58-8722-05b878ba54d5",
            "alertname": "APIRemovedInNextEUSReleaseInUse",
            "alertstate": "firing",
            "group": "policy",
            "prometheus": "openshift-monitoring/k8s",
            "receive": "true",
            "resource": "poddisruptionbudgets",
            "tenant_id": "FB870BF3-9F3A-44FF-9BF7-D7A047A52F43",
            "version": "v1beta1",
        },
        "value": [1677825120.237, "1"],
    },
]

GOOD_FOCS = [
    {
        "metric": {
            "__name__": "cluster_operator_conditions",
            "_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
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
            "tenant_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
        },
        "value": [1677825120.237, "0"],
    },
    {
        "metric": {
            "__name__": "cluster_operator_conditions",
            "_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
            "condition": "Available",
            "endpoint": "metrics",
            "instance": "10.0.142.139:9099",
            "job": "cluster-version-operator",
            "name": "authentication",
            "namespace": "openshift-cluster-version",
            "pod": "cluster-version-operator-6b5c8ff5c8-vrmnl",
            "prometheus": "openshift-monitoring/k8s",
            "receive": "true",
            "service": "cluster-version-operator",
            "tenant_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
        },
        "value": [1677825120.237, "0"],
    },
]

BAD_FOCS = [
    {
        "metric": {
            "__name__": "cluster_operator_conditions",
            "_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
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
            "tenant_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
        },
        "value": [1677825120.237, "0"],
    },
    {
        "metric": {
            "__name__": "cluster_operator_conditions",
            "_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
            "condition": "Available",
            "endpoint": "metrics",
            "instance": "10.0.142.139:9099",
            "job": "cluster-version-operator",
            "namespace": "openshift-cluster-version",
            "pod": "cluster-version-operator-6b5c8ff5c8-vrmnl",
            "prometheus": "openshift-monitoring/k8s",
            "receive": "true",
            "service": "cluster-version-operator",
            "tenant_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
        },
        "value": [1677825120.237, "0"],
    },
    {
        "metric": {
            "__name__": "cluster_operator_conditions",
            "_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
            "endpoint": "metrics",
            "instance": "10.0.142.139:9099",
            "job": "cluster-version-operator",
            "pod": "cluster-version-operator-6b5c8ff5c8-vrmnl",
            "prometheus": "openshift-monitoring/k8s",
            "receive": "true",
            "service": "cluster-version-operator",
            "tenant_id": "813909b1-0a0c-4cda-828b-b34bd26e0196",
        },
        "value": [1677825120.237, "0"],
    },
]


def test_alert():
    """Test the alert can be created and the fields are populated."""
    alert = Alert(name="name", namespace="namespace", severity="severity")

    assert alert.name == "name"
    assert alert.namespace == "namespace"
    assert alert.severity == "severity"


@pytest.mark.parametrize("result_item", GOOD_ALERTS)
def test_parse_metric_to_alert(result_item):
    """Test the alert can be created from a metric obtained from Observatorium."""
    metric = result_item["metric"]
    alert = Alert.parse_metric(metric)

    assert alert.name == metric.get("alertname")
    assert alert.namespace == metric.get("namespace")
    assert alert.severity == metric.get("severity")


@pytest.mark.parametrize("result_item", BAD_ALERTS)
def test_parse_bad_metric_to_alert(result_item):
    """Test that a bad alert cause exceptions when parsing."""
    metric = result_item["metric"]

    with pytest.raises(pydantic.ValidationError):
        Alert.parse_metric(metric)


def test_foc():
    """Test the foc can be created and the fields are populated."""
    foc = FOC(name="name", condition="condition", reason="reason")

    assert foc.name == "name"
    assert foc.condition == "condition"
    assert foc.reason == "reason"


@pytest.mark.parametrize("result_item", GOOD_FOCS)
def test_parse_metric_to_foc(result_item):
    """Test the foc can be created from a metric obtained from Observatorum."""
    metric = result_item["metric"]
    foc = FOC.parse_obj(metric)

    assert foc.name == metric.get("name")
    assert foc.condition == metric.get("condition")
    assert foc.reason == metric.get("reason")


@pytest.mark.parametrize("result_item", BAD_FOCS)
def test_parse_bad_metric_to_foc(result_item):
    """Test that a bad alert cause exceptions when parsing."""
    metric = result_item["metric"]

    with pytest.raises(pydantic.ValidationError):
        FOC.parse_obj(metric)


def test_upgrade_api_response():
    """Test the UpgradeApiResponse can be created and fields are populated."""
    response = UpgradeApiResponse(
        upgrade_recommended=False, upgrade_risks_predictors=EXAMPLE_PREDICTORS
    )
    assert response.upgrade_risks_predictors == EXAMPLE_PREDICTORS


def test_inference_response():
    """Test the InferenceResponse can be created and fields are populated."""
    response = InferenceResponse(upgrade_risks_predictors=EXAMPLE_PREDICTORS)
    assert response.upgrade_risks_predictors == EXAMPLE_PREDICTORS
