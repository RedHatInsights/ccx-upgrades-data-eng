# Upgrade Risks Predictions Data Engineering Service

This is the main reporsitory of the Upgrade Risks Predictions Data Engineering
service. This service was created as part of the
[CCXDEV-9718](https://issues.redhat.com/browse/CCXDEV-9718) epic.

The responsibilities of the data-eng service are:
1. Query RHOBS (a huge Thanos instance that stores the historical metrics of our
customers' clusters) in order to get the latest metrics for a given cluster
([CCXDEV-9850](https://issues.redhat.com/browse/CCXDEV-9850)).
1. Apply a ML model (running in [ccx-upgrades-inference](https://redhat.com/ccx-inference-service))
to select the metrics that are more likely to affect the cluster upgrade.
1. Format the results and return them to the user.

## Configuration

The service will read the following environment variables:

- `CLIENT_ID` (mandatory): The client identifier to get the refresh tokens from SSO server.
- `CLIENT_SECRET` (mandatory): The client secret to get the refresh tokens from SSO server.
- `SSO_ISSUER`: The SSO server that the service will use. By default, it uses https://sso.redhat.com/auth/realms/redhat-external.
- `ALLOW_INSECURE`: If this variable is set to `True`, the SSL certificates signatures won't be checked. It is also needed to export `OAUTHLIB_INSECURE_TRANSPORT=1`. This is useful for locally and BDD testing or if you are using a mocked SSO server or not.
- `RHOBS_URL`: The URL of the Observatorium server. By default, it uses https://observatorium.api.stage.openshift.com.
- `RHOBS_TENANT`: Name of the tenant to be used in the Observatorium endpoint generation. By default, `telemeter` will be used.
- `RHOBS_REQUEST_TIMEOUT`: Number of seconds to use as timeout for the Observatorium requests. By default, it will use `None` (no timeout).
- `INFERENCE_URL`: URL of the inference service.
### Logging configuration

`uvicorn` allows to pass a [Python logging configuration](https://docs.python.org/3/library/logging.config.html#logging-config-fileformat)
to modify the output of the service.

A default one was provided in `logging.yaml` file, that will be used by
the Docker container image.

## Dashboards

Definition of the dashboard for this service and the [inference](https://redhat.com/ccx-inference-service) one is located in [dashboards](dashboards).

## Testing and local development

### Run it locally

Change to the source folder and run the app using `uvicorn`:

```
CLIENT_ID=the-client-id CLIENT_SECRET=the-secret uvicorn ccx_upgrades_data_eng.main:app --reload
```

Note that this command requires valid credentials. If you want to run it against
mocked service, please check how it's done in the [docker-compose.yml](docker-compose.yml).

Then run some requests against the server:

```
curl 'http://127.0.0.1:8000/cluster/34c3ecc5-624a-49a5-bab8-4fdc5e51a266/upgrade-risks-prediction
```

Check the API documentation at http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc.

### Run in docker-compose

Just run `docker-compose up`. Please, check the environment variables defined in
the `ccx-upgrades-data-eng` service to learn more about how it is configured to
use mocked services.

### Run in an ephemeral environment

It is possible to run this service in an ephemeral environment. Just follow the
instructions in [docs/deployment.md]. This way you can check if the app would
work in OCP.

### Unit tests

Unit tests can be run with these commands:

```
source venv/bin/activate
pip install .
pytest -vv
```

### BDD tests

Behaviour tests for this service are included in [Insights Behavioral
Spec](https://github.com/RedHatInsights/insights-behavioral-spec) repository.
In order to run these tests, the following steps need to be made:

1. clone the [Insights Behavioral Spec](https://github.com/RedHatInsights/insights-behavioral-spec) repository
1. go into the cloned subdirectory `insights-behavioral-spec`
1. run the `ccx_upgrade_risk_data_eng_tests.sh` from this subdirectory

List of all test scenarios prepared for this service is available at
<https://redhatinsights.github.io/insights-behavioral-spec/feature_list.html#ccx-upgrades-data-eng>
