"""A set of static examples for the rest of the files."""

EXAMPLE_PREDICTORS = {
    "alerts": [
        {
            "name": "APIRemovedInNextEUSReleaseInUse",
            "namespace": "openshift-kube-apiserver",
            "severity": "info",
        }
    ],
    "operator_conditions": [
        {"name": "authentication", "condition": "Failing", "reason": "AsExpected"}
    ],
}

EXAMPLE_PREDICTORS_WITH_EMPTY_URL = {
    "alerts": [
        {
            "name": "APIRemovedInNextEUSReleaseInUse",
            "namespace": "openshift-kube-apiserver",
            "severity": "info",
            "url": "",
        }
    ],
    "operator_conditions": [
        {"name": "authentication", "condition": "Failing", "reason": "AsExpected", "url": ""}
    ],
}

EXAMPLE_PREDICTORS_WITH_URL = {
    "alerts": [
        {
            "name": "APIRemovedInNextEUSReleaseInUse",
            "namespace": "openshift-kube-apiserver",
            "severity": "info",
            "url": "https://console-openshift-console.some_url.com/monitoring/alerts?orderBy=asc&sortBy=Severity&alert-name=APIRemovedInNextEUSReleaseInUse",
        }
    ],
    "operator_conditions": [
        {
            "name": "authentication",
            "condition": "Failing",
            "reason": "AsExpected",
            "url": "https://console-openshift-console.some_url.com/k8s/cluster/config.openshift.io~v1~ClusterOperator/authentication",
        }
    ],
}

EXAMPLE_ALERT = {
    "name": "APIRemovedInNextEUSReleaseInUse",
    "namespace": "openshift-kube-apiserver",
    "severity": "info",
}

EXAMPLE_FOC = {"name": "authentication", "condition": "Failing", "reason": "AsExpected"}
