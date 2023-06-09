"""Tests to be run by pytest."""

needed_env = {
    "CLIENT_ID": "client-id",
    "CLIENT_SECRET": "secret",
    "INFERENCE_URL": "http://inference:8000",
}

needed_env_cache_enabled = {
    "CLIENT_ID": "client-id",
    "CLIENT_SECRET": "secret",
    "INFERENCE_URL": "http://inference:8000",
    "CACHE_ENABLED": "true",
    "CACHE_TTL": "10",
    "CACHE_SIZE": "10",
}

RHOBS_EMPTY_REPONSE = {
    "status": "success",
    "data": {"resultType": "vector", "result": []},
}

RHOBS_RESPONSE = {
    "status": "success",
    "data": {
        "resultType": "vector",
        "result": [
            # Console URL metric
            {
                "metric": {
                    "__name__": "console_url",
                    "_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "endpoint": "https",
                    "instance": "1.2.3.4:8443",
                    "job": "metrics",
                    "namespace": "openshift-console-operator",
                    "pod": "console-operator-6ff67b94c5-7k2mk",
                    "prometheus": "openshift-monitoring/k8s",
                    "receive": "true",
                    "service": "metrics",
                    "tenant_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "url": "https://console-openshift-console.some_url.com",
                },
                "value": [1677825120.237, "1"],
            },
            # Alert metric
            {
                "metric": {
                    "__name__": "alerts",
                    "_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "alertname": "APIRemovedInNextEUSReleaseInUse",
                    "alertstate": "firing",
                    "group": "batch",
                    "namespace": "openshift-kube-apiserver",
                    "prometheus": "openshift-monitoring/k8s",
                    "receive": "true",
                    "resource": "cronjobs",
                    "severity": "info",
                    "tenant_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "version": "v1beta1",
                },
                "value": [1677825120.237, "1"],
            },
            # FOC metric
            {
                "metric": {
                    "__name__": "cluster_operator_conditions",
                    "_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "condition": "Available",
                    "endpoint": "metrics",
                    "instance": "10.0.142.139:9099",
                    "job": "cluster-version-operator",
                    "name": "authentication",
                    "namespace": "openshift-cluster-version",
                    "pod": "cluster-version-operator-6b5c8ff5c8-vrmnl",
                    "prometheus": "openshift-monitoring/k8s",
                    "reason": "OAuthServerRouteEndpointAccessibleController_EndpointUnavailable",
                    "receive": "true",
                    "service": "cluster-version-operator",
                    "tenant_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                },
                "value": [1677825120.237, "0"],
            },
            # No metric key
            {
                "value": [1677825120.237, "0"],
            },
            # Unexpected metric
            {
                "metric": {
                    "__name__": "an unexpected metric name",
                },
                "value": [1677825120.237, "0"],
            },
        ],
    },
}

RHOBS_RESPONSE_SINGLE_METRIC = {
    "status": "success",
    "data": {
        "resultType": "vector",
        "result": [
            # Console URL metric
            {
                "metric": {
                    "__name__": "console_url",
                    "_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "endpoint": "https",
                    "instance": "1.2.3.4:8443",
                    "job": "metrics",
                    "namespace": "openshift-console-operator",
                    "pod": "console-operator-6ff67b94c5-7k2mk",
                    "prometheus": "openshift-monitoring/k8s",
                    "receive": "true",
                    "service": "metrics",
                    "tenant_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "url": "https://console-openshift-console.some_url.com",
                },
                "value": [1677825120.237, "1"],
            },
            # FOC metric
            {
                "metric": {
                    "__name__": "cluster_operator_conditions",
                    "_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                    "condition": "Available",
                    "endpoint": "metrics",
                    "instance": "10.0.142.139:9099",
                    "job": "cluster-version-operator",
                    "name": "authentication",
                    "namespace": "openshift-cluster-version",
                    "pod": "cluster-version-operator-6b5c8ff5c8-vrmnl",
                    "prometheus": "openshift-monitoring/k8s",
                    "reason": "OAuthServerRouteEndpointAccessibleController_EndpointUnavailable",
                    "receive": "true",
                    "service": "cluster-version-operator",
                    "tenant_id": "34c3ecc5-624a-49a5-bab8-4fdc5e51a266",
                },
                "value": [1677825120.237, "0"],
            },
        ],
    },
}
