"""Models to be used in the REST API."""

from typing import Any, List, Optional, Type
from uuid import UUID

from pydantic import ConfigDict, BaseModel  # pylint: disable=no-name-in-module
from datetime import datetime

from ccx_upgrades_data_eng.examples import (
    EXAMPLE_ALERT,
    EXAMPLE_FOC,
    EXAMPLE_PREDICTORS,
    EXAMPLE_PREDICTORS_WITH_URL,
)


class Alert(BaseModel):  # pylint: disable=too-few-public-methods
    """Alert containing name, namespace and severity."""

    name: str
    namespace: Optional[str] = None
    severity: str
    model_config = ConfigDict(json_schema_extra={"example": {"alert": EXAMPLE_ALERT}})

    @classmethod
    def parse_metric(cls: Type["Model"], obj: Any) -> "Model":  # noqa
        """Wrap the parsing of an Observatorium metric object and return an Alert"""
        obj = obj.copy()  # dont modify the original obj
        if "alertname" in obj:
            obj["name"] = obj["alertname"]

        return Alert.model_validate(obj)

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
    reason: Optional[str] = None
    model_config = ConfigDict(json_schema_extra={"example": {"foc": EXAMPLE_FOC}})

    @classmethod
    def parse_metric(cls: Type["Model"], obj: Any) -> "Model":  # noqa
        """Wrap the parsing of an Observatorium metric object and return a FOC"""
        obj = obj.copy()  # dont modify the original obj
        if "condition" in obj:
            if obj["condition"] == "Available":
                # because the rhobs query looks for
                # cluster_operator_conditions{{condition="Available"}} == 0
                # it is needed to update the condition to match
                obj["condition"] = "Not Available"

        return FOC.model_validate(obj)

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

    def __hash__(self):
        """Needed in order to cache functions that use this model."""
        return hash(
            (
                "alerts",
                tuple(self.alerts),
                "operator_conditions",
                tuple(self.operator_conditions),
            )
        )

    def remove_duplicates(self):
        """Remove the duplicates from the alerts and focs."""
        self.alerts = list(set(self.alerts))
        self.operator_conditions = list(set(self.operator_conditions))


class InferenceResponse(BaseModel):
    """The response obtained from the inference service."""

    upgrade_risks_predictors: UpgradeRisksPredictors
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "upgrade_risks_predictors": EXAMPLE_PREDICTORS,
            }
        }
    )


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
    last_checked_at: datetime

    def __hash__(self):
        """Needed in order to cache functions that use this model."""
        return hash(
            (
                "upgrade_recommended",
                self.upgrade_recommended,
                "upgrade_risks_predictors",
                self.upgrade_risks_predictors,
            )
        )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "upgrade_recommended": False,
                "upgrade_risks_predictors": EXAMPLE_PREDICTORS_WITH_URL,
            }
        }
    )


class ClusterPrediction(BaseModel):
    """
    ClusterPrediction is an element of the response for the upgrade-risks-prediction endpoint for multiple clusters.

    Contains the prediction for a single cluster, like UpgradeApiResponse, but including 2 extra fields: cluster_id and
    prediction_status. The later is to indicate if the prediction was performed correctly, not the result of the
    prediction.
    """

    cluster_id: str
    prediction_status: str
    upgrade_recommended: Optional[bool] = None
    upgrade_risks_predictors: Optional[UpgradeRisksPredictorsWithURLs] = None
    last_checked_at: Optional[datetime] = None


class MultiClusterUpgradeApiResponse(BaseModel):
    """
    MultiClusterUpgradeApiResponse is the response for the upgrade-risks-prediction endpoint for multiple clusters.

    Contain the result of the prediction for each cluster: whether the upgrade will fail or not;
    and the predictors that the model detected as actual risks.
    """

    predictions: List[ClusterPrediction]
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predictions": [
                    {
                        "cluster_id": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                        "prediction_status": "ok",
                        "upgrade_recommended": True,
                        "upgrade_risks_predictors": {
                            "alerts": [],
                            "operator_conditions": [],
                        },
                        "last_checked_at": "2011-15-04T00:05:23Z",
                    },
                ],
            }
        }
    )


class ClustersList(BaseModel):
    """
    ClustersList is the definition for the request body for the upgrade-risk-prediction endpoint.

    It allows to include an array of cluster ids from the request.
    """

    clusters: List[UUID]
