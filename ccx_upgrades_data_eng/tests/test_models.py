"""Test models.py."""

from ccx_upgrades_data_eng.models import Alert, FOC, UpgradeApiResponse
from ccx_upgrades_data_eng.examples import EXAMPLE_PREDICTORS


def test_alert():
    """Test the alert can be created and the fields are populated."""
    alert = Alert(name="name", namespace="namespace", severity="severity")

    assert alert.name == "name"
    assert alert.namespace == "namespace"
    assert alert.severity == "severity"


def test_foc():
    """Test the foc can be created and the fields are populated."""
    foc = FOC(name="name", condition="condition", reason="reason")

    assert foc.name == "name"
    assert foc.condition == "condition"
    assert foc.reason == "reason"


def test_upgrade_api_response():
    """Test the UpgradeApiResponse can be created and fields are populated."""
    response = UpgradeApiResponse(
        upgrade_recommended=False, upgrade_risks_predictors=EXAMPLE_PREDICTORS
    )
    assert response.upgrade_risks_predictors == EXAMPLE_PREDICTORS
