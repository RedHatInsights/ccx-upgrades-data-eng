"""Utility functions to fill the alerts and focs with urls to console."""

from urllib.parse import urljoin
from ccx_upgrades_data_eng.models import UpgradeApiResponse


def fill_urls(response: UpgradeApiResponse, console_url: str):
    """Fill the alerts and FOCs with a link to the console URL."""
    if console_url == "":
        return

    for alert in response.upgrade_risks_predictors.alerts:
        if alert.name == "":
            continue
        alert.url = urljoin(
            console_url, f"/monitoring/alerts?orderBy=asc&sortBy=Severity&alert-name={alert.name}"
        )

    for foc in response.upgrade_risks_predictors.operator_conditions:
        if foc.name == "":
            continue
        foc.url = urljoin(
            console_url, f"/k8s/cluster/config.openshift.io~v1~ClusterOperator/{foc.name}"
        )
