"""Tests for the urls module."""

from ccx_upgrades_data_eng.models import UpgradeApiResponse
from ccx_upgrades_data_eng.examples import (
    EXAMPLE_PREDICTORS,
    EXAMPLE_PREDICTORS_WITH_URL,
    EXAMPLE_DATE,
)
from ccx_upgrades_data_eng.urls import fill_urls


def test_fill_urls_with_console_url():
    """Check the urls are filled correctly."""
    response = UpgradeApiResponse(
        upgrade_recommended=False,
        upgrade_risks_predictors=EXAMPLE_PREDICTORS,
        last_checked_at=EXAMPLE_DATE,
    )
    fill_urls(response, console_url="https://console-openshift-console.some_url.com")
    assert response == UpgradeApiResponse(
        upgrade_recommended=False,
        upgrade_risks_predictors=EXAMPLE_PREDICTORS_WITH_URL,
        last_checked_at=EXAMPLE_DATE,
    )


def test_fill_urls_no_console_url():
    """Check the urls are not filled if the console url is empty."""
    response = UpgradeApiResponse(
        upgrade_recommended=False,
        upgrade_risks_predictors=EXAMPLE_PREDICTORS,
        last_checked_at=EXAMPLE_DATE,
    )
    fill_urls(response, console_url="")
    assert response == UpgradeApiResponse(
        upgrade_recommended=False,
        upgrade_risks_predictors=EXAMPLE_PREDICTORS,
        last_checked_at=EXAMPLE_DATE,
    )


def test_fill_urls_with_console_url_no_names():
    """Check the urls are not added for alerts/FOCs without name."""
    predictors = {
        "alerts": [
            {
                "name": "",
                "namespace": "openshift-kube-apiserver",
                "severity": "info",
            }
        ],
        "operator_conditions": [{"name": "", "condition": "Failing", "reason": "AsExpected"}],
    }
    expected = {
        "alerts": [
            {
                "name": "",
                "namespace": "openshift-kube-apiserver",
                "severity": "info",
                "url": "",
            }
        ],
        "operator_conditions": [
            {"name": "", "condition": "Failing", "reason": "AsExpected", "url": ""}
        ],
    }
    response = UpgradeApiResponse(
        upgrade_recommended=False,
        upgrade_risks_predictors=predictors,
        last_checked_at=EXAMPLE_DATE,
    )
    fill_urls(response, console_url="https://console-openshift-console.some_url.com")
    assert response == UpgradeApiResponse(
        upgrade_recommended=False,
        upgrade_risks_predictors=expected,
        last_checked_at=EXAMPLE_DATE,
    )
