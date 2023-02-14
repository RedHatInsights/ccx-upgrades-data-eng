# Upgrade Risks Predictions Data Engineering Service

This is the main reporsitory of the Upgrade Risks Predictions Data Engineering
service.

Related Jira: [CCXDEV-9718](https://issues.redhat.com/browse/CCXDEV-9718)

## Configuration

The service will read the following environment variables:

- `CLIENT_ID` (mandatory): The client identifier to get the refresh tokens from SSO server.
- `CLIENT_SECRET` (mandatory): The client secret to get the refresh tokens from SSO server.
- `SSO_ISSUER`: The SSO server that the service will use. By default, it uses https://sso.redhat.com/auth/realms/redhat-external.
- `RHOBS_URL`: The URL of the Observatorium server. By default, it uses https://observatorium.api.stage.openshift.com.
- `RHOBS_TENANT`: Name of the tenant to be used in the Observatorium endpoint generation. By default, `telemeter` will be used.
- `RHOBS_REQUEST_TIMEOUT`: Number of seconds to use as timeout for the Observatorium requests. By default, it will use `None` (no timeout).

### Logging configuration

`uvicorn` allows to pass a [Python logging configuration](https://docs.python.org/3/library/logging.config.html#logging-config-fileformat)
to modify the output of the service.

A default one was provided in `logging.yaml` file, that will be used by 
the Docker container image.

## Run it locally

Change to the source folder and run the app using `uvicorn`:

```
CLIENT_ID=the-client-id CLIENT_SECRET=the-secret uvicorn ccx_upgrades_data_eng.main:app --reload
```

Then run some requests against the server:

```
curl 'http://127.0.0.1:8000/upgrade-risks-prediction/?cluster_id=34c3ecc5-624a-49a5-bab8-4fdc5e51a266'
```

Check the API documentation at http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc.
