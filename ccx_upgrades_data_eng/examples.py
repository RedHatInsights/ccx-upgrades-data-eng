"""A set of static examples for the rest of the files."""

ALERT_NAME = "APIRemovedInNextEUSReleaseInUse"

FOC_NAME = "authentication"

EXAMPLE_DATE = "0001-01-01T00:00:00Z"
EXAMPLE_CLUSTER_ID = "b0b3b9ce-d3b9-4eec-b13d-241dffdb1395"

EXAMPLE_ALERT = {
    "name": ALERT_NAME,
    "namespace": "openshift-kube-apiserver",
    "severity": "info",
}

EXAMPLE_FOC = {"name": FOC_NAME, "condition": "Failing", "reason": "AsExpected"}

EXAMPLE_CONSOLE_URL = "https://console-openshift-console.some_url.com"

URL_ALERT = (
    EXAMPLE_CONSOLE_URL + "/monitoring/alerts?orderBy=asc&sortBy=Severity&alert-name=" + ALERT_NAME
)

URL_OPERATOR_CONDITIONS = (
    EXAMPLE_CONSOLE_URL + "/k8s/cluster/config.openshift.io~v1~ClusterOperator/" + FOC_NAME
)

EXAMPLE_PREDICTORS = {
    "alerts": [EXAMPLE_ALERT],
    "operator_conditions": [EXAMPLE_FOC],
}

EXAMPLE_PREDICTORS_WITH_EMPTY_URL = {
    "alerts": [
        {
            "name": ALERT_NAME,
            "namespace": "openshift-kube-apiserver",
            "severity": "info",
            "url": "",
        }
    ],
    "operator_conditions": [
        {"name": FOC_NAME, "condition": "Failing", "reason": "AsExpected", "url": ""}
    ],
}

EXAMPLE_PREDICTORS_WITH_URL = {
    "alerts": [
        {
            "name": ALERT_NAME,
            "namespace": "openshift-kube-apiserver",
            "severity": "info",
            "url": URL_ALERT,
        }
    ],
    "operator_conditions": [
        {
            "name": FOC_NAME,
            "condition": "Failing",
            "reason": "AsExpected",
            "url": URL_OPERATOR_CONDITIONS,
        }
    ],
}
