# Clowder configuration

As this service is deployed using the console.redhat.com AppSRE
platform, some specific values for infrastructure services are
provided via Clowder configuration.

## Which values can be expected in a Clowder configuration file

In the case of CCX Data Pipeline Archives Handler, the only
infrastructure to take into account is the Kafka broker. The hostname,
port, securty protocol, SSL certificate (if any) and SASL
credentials are provided via Clowder, so the service **overwrites**
the default configuration 

## How does the platform provide the Clowder configuration?

The platform mounts a directory in every pod (currently in `/cdapp`),
that contains several files. The Clowder configuration is in one of
them and it's a JSON file. See an example bellow:

```json
{
  "BOPURL": "http://env-ephemeral-r5rhif-mbop.ephemeral-XXXXXX.svc:8090",
  "endpoints": [
    {
      "app": "ingress",
      "hostname": "ingress-service.ephemeral-r5rhif.svc",
      "name": "service",
      "port": 8000
    }
  ],
  "featureFlags": {
    "hostname": "env-ephemeral-r5rhif-featureflags.ephemeral-r5rhif.svc",
    "port": 4242,
    "scheme": "http"
  },
  "kafka": {
    "brokers": [
      {
        "hostname": "test-kafka-cbt-e---jei-s--i---a.bf2.kafka.rhcloud.com",
        "port": 443,
        "authtype": "sasl",
        "sasl": {
          "username": "b99710cf-f92c-41b5-9f74-41dcab32a013",
          "password": "C9wbMeJGwkUx8VGD1nQWw7Wr8YhhW2T7"
        }
      }
    ],
    "topics": [
      {
        "name": "platform.upload.buckit",
        "requestedName": "platform.upload.buckit"
      },
      {
        "name": "ccx.ocp.results",
        "requestedName": "ccx.ocp.results"
      },
      {
        "name": "platform.payload-status",
        "requestedName": "platform.payload-status"
      }
    ]
  },
  "logging": {
    "cloudwatch": {
      "accessKeyId": "",
      "logGroup": "",
      "region": "",
      "secretAccessKey": ""
    },
    "type": "null"
  },
  "metadata": {
    "deployments": [
      {
        "image": "quay.io/cloudservices/ccx-data-pipeline:0a0f400",
        "name": "archives-handler"
      }
    ],
    "envName": "env-ephemeral-r5rhif",
    "name": "ccx-data-pipeline"
  },
  "metricsPath": "/metrics",
  "metricsPort": 9000,
  "privatePort": 10000,
  "publicPort": 8000,
  "webPort": 8000
}
```

## How can we deal with the Clowder configuration file?

In order to unify the way the services access this configuration
file, the platform provides several libraries in different programming
languages in order to parse the configuration file and provides a data
structure with all the important values already parsed.

In our case, all the hard work is done in our
`ccx_messaging.utils.clowder` library, which uses the platform
library to read the Clowder configuration file and mix it with the
values provided to the [service configuration](configuration).

# CCX Data Pipeline specific relevant values

The consumer, publisher and Payload Tracker watcher (if enabled)
configurations should be updated with the following Kafka
configurations from Clowder:

- Kafka broker URL (hostname and port)
- Kafka Security protocol
- Kafka SASL mechanism
- Kafka SASL username
- Kafka SASL password
- Kafka SSL certificate (if any is provided)

## Kafka topics

When a service is defined to be used in the platform, it should
declare which Kafka topics it needs to work. The platform will create
the topics if needed and it will give a name in the Kafka instance
that can differ from the requested one.

For that reason, the services running in the platform should look into
the Clowder configuration for the mapping between requested topic
names and the real ones created by the platform, so the service should
use the later in order to consume or publish messages into them.

For the CCX Data Pipeline Archives Handler, the consumer, the publisher and the Payload Tracker watcher configurations should be
updated to use the real name instead of the requested name.
