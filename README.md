test

# dvo-extractor
DVO extractor service based on CCX Messaging

## Ephemeral deployment for debugging

1. Install `bonfire`
```
pip install crc-bonfire
```

2. Log into https://console-openshift-console.apps.c-rh-c-eph.8p0c.p1.openshiftapps.com/k8s/cluster/projects

```
oc login --token=${TOKEN} --server=https://api.c-rh-c-eph.8p0c.p1.openshiftapps.com:6443
```

3. Reserve a namespace
```
NAMESPACE=$(bonfire namespace reserve)
```

4. Deploy the clowdapp
```
bonfire deploy -c deploy/test.yaml -n $NAMESPACE --component dvo-extractor ccx-data-pipeline
```

5. Check the resource via CLI or UI.

6. Delete the namespace
```
bonfire namespace release $NAMESPACE 
```
