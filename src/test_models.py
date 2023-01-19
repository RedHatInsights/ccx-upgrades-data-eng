"""Test models.py."""

from models import Alert, FOC, UpgradeApiResponse


def test_alert():
    alert = Alert(
        name = "name",
        namespace = "namespace",
        severity = "severity"
    )

    assert alert.name == "name"
    assert alert.namespace == "namespace"
    assert alert.severity == "severity"

def test_foc():
    foc = FOC(
        name = "name",
        condition = "condition",
        reason = "reason"
    )

    assert foc.name == "name"
    assert foc.condition == "condition"
    assert foc.reason == "reason"

def test_upgrade_api_response():
    response = UpgradeApiResponse(
        upgrade_recommended=False,
        upgrade_risks_predictors={
            "alerts": [
                {
                    "name": "APIRemovedInNextEUSReleaseInUse",
                    "namespace": "openshift-kube-apiserver",
                    "severity": "info"
                }
            ],
            "operator_conditions": [
                {
                    "name": "authentication",
                    "condition": "Failing",
                    "reason": "AsExpected"
                }
            ]
        }
    )