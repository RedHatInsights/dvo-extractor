# CCX Data Pipeline

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

## Description

This service will receive records from a given Kafka topic, download the items
from the S3 server and apply Insights rules to downloaded tarball.

JSON containing Insights rules results will be sent to a different Kafka topic
and logged in a way to be determined.

Incoming and outgoing Kafka topics are configurable, these can be even handled
by different Kafka instances.

## Architecture

This service is built on top of [insights-core-messaging framework](https://github.com/RedHatInsights/insights-core-messaging)
and will be deployed and run inside [cloud.redhat.com](https://cloud.redhat.com).

### External data pipeline diagram

![diagram](./doc/external_pipeline_diagram.jpg)

### Sequence diagram

![sequence](./doc/sequence-diagram.png)

### Whole data flow

![data_flow](./doc/customer_facing_services_architecture.png)

1. Event about new data from insights operator is consumed from Kafka. That event contains (among other things) URL to S3 Bucket
2. Insights operator data is read from S3 Bucket and insigts rules are applied to that data
3. Results (basically organization ID + cluster name + insights results JSON) are stored back into Kafka, but into different topic
4. That results are consumed by Insights rules aggregator service that caches them
5. The service provides such data via REST API to other tools, like OpenShift Cluster Manager web UI, OpenShift console, etc.

## Modules

### Data consumer

Every time a new record is sent by Kafka to the subscribes topic, the `KafkaConsumer` will handle and process it,
recovering from the corresponding S3 bucket, and passing the downloaded file to the `Engine` in order to process it.

### Processing

The ICM `Engine` class will take the downloaded tarball and, using **ccx-ocp-core** and **ccx-rules-ocp**, process it
and generates a JSON report. This report will be handled and sent to a configured Kafka topic using a `KafkaPublisher`.


### Reporting

The JSON report generated in the previous step will be sent to a Kafka topic where other services can take this record
and handle it properly.

### Format of the notified Kafka records

```
{
  "account": ACCOUNT_ID (uint),
  "principal": (uint),
  "size": 55099,
  "url": "https://insights-dev-upload-perm.s3.amazonaws.com/e927438c126040dab7891608447da0b5?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJW4PUHKGSOIEEI7A%2F20200123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20200123T161559Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=3e123beac8503f4338f611f85b053f7f15e69e2748228f9f98b6986e7c06fb6c",
  "b64_identity": "eyJlbnRpdGxlbWVudHMiOnsiaW5zaWdodHMiOnsiaXNfZW50aXRsZWQiOnRydWV9LCJjb3N0X21hbmFnZW1lbnQiOnsiaXNfZW50aXRsZWQiOnRydWV9LCJhbnNpYmxlIjp7ImlzX2VudGl0bGVkIjp0cnVlfSwib3BlbnNoaWZ0Ijp7ImlzX2VudGl0bGVkIjp0cnVlfSwic21hcnRfbWFuYWdlbWVudCI6eyJpc19lbnRpdGxlZCI6dHJ1ZX0sIm1pZ3JhdGlvbnMiOnsiaXNfZW50aXRsZWQiOnRydWV9fSwiaWRlbnRpdHkiOnsiaW50ZXJuYWwiOnsiYXV0aF90aW1lIjoxNDAwLCJvcmdfaWQiOiIxMjM4MzAzMiJ9LCJhY2NvdW50X251bWJlciI6IjYyMTIzNzciLCJhdXRoX3R5cGUiOiJiYXNpYy1hdXRoIiwidXNlciI6eyJmaXJzdF9uYW1lIjoiSW5zaWdodHMiLCJpc19hY3RpdmUiOnRydWUsImlzX2ludGVybmFsIjpmYWxzZSwibGFzdF9uYW1lIjoiUUUiLCJsb2NhbGUiOiJlbl9VUyIsImlzX29yZ19hZG1pbiI6dHJ1ZSwidXNlcm5hbWUiOiJpbnNpZ2h0cy1xZSIsImVtYWlsIjoiam5lZWRsZStxYUByZWRoYXQuY29tIn0sInR5cGUiOiJVc2VyIn19",
  "timestamp": "2020-01-23T16:15:59.478901889Z"
}
```

The attribute `b64_identity` contains another JSON encoded by BASE64 encoding. User and org identities are stored here:

```
...
...
...
    "identity": {
        "account_number": "6212377",
        "auth_type": "basic-auth",
        "internal": {
            "auth_time": 1400,
            "org_id": "12383032"
        },
        "type": "User",
        "user": {
            "email": "jneedle+qa@redhat.com",
            "first_name": "Insights",
            "is_active": true,
            "is_internal": false,
            "is_org_admin": true,
            "last_name": "QE",
            "locale": "en_US",
            "username": "insights-qe"
        }
...
...
...

```

### Format of the logs

TBD

## Implementation

To be described

## Usage

First you need to start Kafka, through `docker-compose`:

```shell
docker-compose up -d
```

Second step is to install python dependencies:

```shell
pip install -e .
```

Third step is to start controller:

```shell
python -u -m insights_messaging config.yaml
```

## Configuration

The `config.yaml` is an standard **Insights Core Messaging** configuration file. To learn
about its structure and configuring some common things, you probably want to read its
documentation:
[Insights Core Messaging documentation](https://github.com/RedHatInsights/insights-core-messaging#example-configuration).

Some of the specific **ccx-data-pipeline** configuration points are in the `service` section, where
the specific _consumer_, _downloader_ and _publisher_ are configured.
- `consumer` name refers to the class `controller.consumer.Consumer`. The arguments passed to the initializer
  are defined in the `kwargs` dictionary:
  initializer. The most relevants are:
  - `incoming_topic`: the Kafka topic to subscribe the consumer object.
  - `incoming_topic_env`: an environment variable that will store a Kafka topic to subscribe.
    This option takes precedence over the previous one.
  - `group_id`: Kafka group identifier. Several instances of the same pipeline will need to be into
    the same group in order to not process the same messages.
  - `group_id_env`: the name of an environment variable that will store the same as the previous option.
    It takes precedence over `group_id`.
  - `bootstrap_servers`: a list of "IP:PORT" strings where the Kafka server is listening.
  - `bootstrap_server_env`: The name of an environment variable that stores the endpoint of a Kafka
    server. It takes precedence over `boostrap_servers`, but it only allows to define one server.
- `publisher` name refers to the class `controller.publisher.Publisher` and it also allow to define the
  arguments passed to the initializer modifying the `kwargs` dictionary:
  - `outgoing_topic`: a string indicating the topic where the reported results should be sent.
  - `outgoing_topic_env`: environment variable name that stores the same option described in
    `outgoing_topic`. It takes precedence over it.
  - `bootstrap_servers`: same as in `consumer`, a list of Kafka servers to connect
  - `bootstrap_server_env`: same as in `consumer`. Takes precedence over the previous one.
- `watchers`: it has a list of `Watcher` objects that will receive notifications of events during the
  pipeline processing steps. The configured one is serving statistics for a
  [Prometehus service](https://prometheus.io/).
