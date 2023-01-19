"""Models to be used in the REST API."""

from typing import List
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from ccx_upgrades_data_eng.examples import EXAMPLE_ALERT, EXAMPLE_FOC, EXAMPLE_PREDICTORS


class Alert(BaseModel):  # pylint: disable=too-few-public-methods
    """Alert containing name, namespace and severity."""

    name: str
    namespace: str
    severity: str

    class Config:  # pylint: disable=too-few-public-methods
        """Update the configuration with an example."""

        schema_extra = {"example": {"alert": EXAMPLE_ALERT}}


class FOC(BaseModel):  # pylint: disable=too-few-public-methods
    """Failing Operator Condition containing name, condition and reason."""

    name: str
    condition: str
    reason: str

    class Config:  # pylint: disable=too-few-public-methods
        """Update the configuration with an example."""

        schema_extra = {"example": {"foc": EXAMPLE_FOC}}


class UpgradeRisksPredictors(BaseModel):
    """A dict containing list of alerts and FOCs."""

    alerts: List[Alert]
    operator_conditions: List[FOC]


class UpgradeApiResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """
    UpgradeApiResponse is the response for the upgrade-risks-prediction endpoint.

    Contain the result of the prediction: whether the upgrade will fail or not; and
    the predictors that the model detected as actual risks.
    """

    upgrade_recommended: bool
    upgrade_risks_predictors: UpgradeRisksPredictors

    class Config:  # pylint: disable=too-few-public-methods
        """Update the configuration with an example."""

        schema_extra = {
            "example": {
                "upgrade_recommended": False,
                "upgrade_risks_predictors": EXAMPLE_PREDICTORS,
            }
        }
