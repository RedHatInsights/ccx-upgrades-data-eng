"""Custom Prometheus metrics."""

import logging

from prometheus_client import Counter, Histogram
from prometheus_client.utils import INF

from ccx_upgrades_data_eng.models import UpgradeApiResponse

logger = logging.getLogger(__name__)

CCX_UPGRADES_PREDICTION_TOTAL = Counter(
    "ccx_upgrades_prediction_total",
    "Number of upgrades predictions.",
    labelnames=("recommendation",),
)

CCX_UPGRADES_RISKS_TOTAL = Histogram(
    "ccx_upgrades_risks_total",
    "Number of risks.",
    labelnames=("type",),
    buckets=(0.005, 1, 2, 5, 10, 25, 50, 100, INF),
)

CCX_UPGRADES_RHOBS_TIME = Histogram(
    "ccx_upgrades_rhobs_time",
    "Time to query RHOBS.",
)


def update_ccx_upgrades_prediction_total(response: UpgradeApiResponse):
    """Update CCX_UPGRADES_PREDICTION_TOTAL."""
    if response.upgrade_recommended:
        CCX_UPGRADES_PREDICTION_TOTAL.labels("success").inc()
    else:
        CCX_UPGRADES_PREDICTION_TOTAL.labels("failure").inc()


def update_ccx_upgrades_risks_total(response: UpgradeApiResponse):
    """Update CCX_UPGRADES_RISKS_TOTAL."""
    CCX_UPGRADES_RISKS_TOTAL.labels("alerts").observe(len(response.upgrade_risks_predictors.alerts))
    CCX_UPGRADES_RISKS_TOTAL.labels("operator_conditions").observe(
        len(response.upgrade_risks_predictors.operator_conditions)
    )


def update_ccx_upgrades_rhobs_time(elapsed: float):
    """Update CCX_UPGRADES_RHOBS_TIME."""
    CCX_UPGRADES_RHOBS_TIME.observe(elapsed)
