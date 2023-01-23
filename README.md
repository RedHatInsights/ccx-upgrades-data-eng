# Upgrade Risks Predictions Data Engineering Service

This is the main reporsitory of the Upgrade Risks Predictions Data Engineering
service.

Related Jira: [CCXDEV-9718](https://issues.redhat.com/browse/CCXDEV-9718)

## Run it locally

Change to the source folder and run the app using `uvicorn`:

```
uvicorn ccx_upgrades_data_eng.main:app --reload
```

Then run some requests against the server:

```
curl 'http://127.0.0.1:8000/upgrade-risks-prediction/?cluster_id=34c3ecc5-624a-49a5-bab8-4fdc5e51a266'
```

Check the API documentation at http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc.
