"""Models to be used in the REST API."""

from typing import Any, List, Optional, Type
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from ccx_upgrades_data_eng.examples import (
    EXAMPLE_ALERT,
    EXAMPLE_FOC,
    EXAMPLE_PREDICTORS,
    EXAMPLE_PREDICTORS_WITH_URL,
)


class Alert(BaseModel):  # pylint: disable=too-few-public-methods
    """Alert containing name, namespace and severity."""

    name: str
    namespace: Optional[str]
    severity: str

    class Config:  # pylint: disable=too-few-public-methods
        """Update the configuration with an example."""

        schema_extra = {"example": {"alert": EXAMPLE_ALERT}}

    @classmethod
    def parse_metric(cls: Type["Model"], obj: Any) -> "Model":  # noqa
        """Wrap the parsing of an Observatorium metric object and return an Alert"""
        if "alertname" in obj:
            obj["name"] = obj["alertname"]

        return Alert.parse_obj(obj)

    def __eq__(self, other):
        """Needed in order to remove duplicates from a list of alerts."""
        return (
            self.name == other.name
            and self.namespace == other.namespace
            and self.severity == other.severity
        )

    def __hash__(self):
        """Needed in order to remove duplicates from a list of focs."""
        return hash(("name", self.name, "namespace", self.namespace, "severity", self.severity))


class FOC(BaseModel):  # pylint: disable=too-few-public-methods
    """Failing Operator Condition containing name, condition and reason."""

    name: str
    condition: str
    reason: Optional[str]

    class Config:  # pylint: disable=too-few-public-methods
        """Update the configuration with an example."""

        schema_extra = {"example": {"foc": EXAMPLE_FOC}}

    def __eq__(self, other):
        """Needed in order to remove duplicates from a list of focs."""
        return (
            self.name == other.name
            and self.condition == other.condition
            and self.reason == other.reason
        )

    def __hash__(self):
        """Needed in order to remove duplicates from a list of focs."""
        return hash(("name", self.name, "condition", self.condition, "reason", self.reason))


class UpgradeRisksPredictors(BaseModel):
    """A dict containing list of alerts and FOCs."""

    alerts: List[Alert]
    operator_conditions: List[FOC]

    def remove_duplicates(self):
        """Remove the duplicates from the alerts and focs."""
        self.alerts = list(set(self.alerts))
        self.operator_conditions = list(set(self.operator_conditions))


class InferenceResponse(BaseModel):
    """The response obtained from the inference service."""

    upgrade_risks_predictors: UpgradeRisksPredictors

    class Config:  # pylint: disable=too-few-public-methods
        """Update the configuration with an example."""

        schema_extra = {
            "example": {
                "upgrade_risks_predictors": EXAMPLE_PREDICTORS,
            }
        }


class AlertWithURL(Alert):
    """An alert filled with its link to console url."""

    url: str = ""


class FOCWithURL(FOC):
    """An Failing Operator Condition filled with its link to console url."""

    url: str = ""


class UpgradeRisksPredictorsWithURLs(BaseModel):
    """A dict containing list of alerts and FOCs."""

    alerts: List[AlertWithURL]
    operator_conditions: List[FOCWithURL]


class UpgradeApiResponse(BaseModel):  # pylint: disable=too-few-public-methods
    """
    UpgradeApiResponse is the response for the upgrade-risks-prediction endpoint.

    Contain the result of the prediction: whether the upgrade will fail or not;
    and the predictors that the model detected as actual risks.
    """

    upgrade_recommended: bool
    upgrade_risks_predictors: UpgradeRisksPredictorsWithURLs

    class Config:  # pylint: disable=too-few-public-methods
        """Update the configuration with an example."""

        schema_extra = {
            "example": {
                "upgrade_recommended": False,
                "upgrade_risks_predictors": EXAMPLE_PREDICTORS_WITH_URL,
            }
        }
