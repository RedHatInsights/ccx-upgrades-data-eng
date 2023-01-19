# Deployment

## Testing the local version of the service in an ephemeral cluster

**VPN needed!**

1. Install `bonfire`
```
pip install crc-bonfire
```

2. Log into ephemeral cluster

```
oc login --token=${TOKEN} --server=<ephemeral cluster>
```

3. Reserve a namespace
```
export NAMESPACE=$(bonfire namespace reserve)
```

4. Deploy the renderer
```
bonfire deploy -c deploy/test.yaml -n $NAMESPACE ccx-upgrades-data-eng
```

5. Check the pod is deployed

```
POD=`oc --namespace $NAMESPACE get pods | grep ccx-upgrades-data-eng | awk '{print $1}'`
oc --namespace $NAMESPACE logs $POD
```

6. Make a request to the renderer

Launch a debugging pod with curl installed:
```
oc --namespace $NAMESPACE run curl -i --tty --rm \
    --image=docker.io/curlimages/curl:latest -- sh
```

Wait for the command prompt. Then run some requests:

```
curl -s -X 'GET' \
    'ccx-upgrades-data-eng-svc:8000/upgrade-risks-prediction' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/json' \
    -d '{"risks": ["foc|machine-config|Available"]}'
```

You should see the response. Exit the container using `CTRL+D` or `exit`. The 
pod is automatically deleted.

6. Delete the namespace

```
bonfire namespace release $NAMESPACE 
```