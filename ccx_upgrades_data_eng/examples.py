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

EXAMPLE_ALERT = {
    "name": "APIRemovedInNextEUSReleaseInUse",
    "namespace": "openshift-kube-apiserver",
    "severity": "info",
}

EXAMPLE_FOC = {"name": "authentication", "condition": "Failing", "reason": "AsExpected"}
