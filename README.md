# CCX Data Pipeline

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

## Description

This service will receive records from a given Kafka topic, download the items
from the S3 server and apply Insights rules to downloaded tarball.

JSON containing Insights rules results will be sent to a different Kafka topic
and logged in a way to be determined.

Incoming and outgoing Kafka topics are configurable, these can be even handled
by different Kafka instances.

### Integration with other services

Please look at [CCX Docs/Customer
Services](https://ccx-docs.cloud.paas.psi.redhat.com//customer/index.html) with
an explanation how the CCX Data Pipeline is connected with other services.

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

#### Format of the received Kafka records

```
{
  "account": 123456, // (uint)
  "principal": 9, // (uint)
  "size": 55099, // (uint)
  "url": "https://insights-dev-upload-perm.s3.amazonaws.com/e927438c126040dab7891608447da0b5?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAJW4PUHKGSOIEEI7A%2F20200123%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20200123T161559Z&X-Amz-Expires=86400&X-Amz-SignedHeaders=host&X-Amz-Signature=3e123beac8503f4338f611f85b053f7f15e69e2748228f9f98b6986e7c06fb6c", // (string)
  "b64_identity": "eyJlbnRpdGxlbWVudHMiOnsiaW5zaWdodHMiOnsiaXNfZW50aXRsZWQiOnRydWV9LCJjb3N0X21hbmFnZW1lbnQiOnsiaXNfZW50aXRsZWQiOnRydWV9LCJhbnNpYmxlIjp7ImlzX2VudGl0bGVkIjp0cnVlfSwib3BlbnNoaWZ0Ijp7ImlzX2VudGl0bGVkIjp0cnVlfSwic21hcnRfbWFuYWdlbWVudCI6eyJpc19lbnRpdGxlZCI6dHJ1ZX0sIm1pZ3JhdGlvbnMiOnsiaXNfZW50aXRsZWQiOnRydWV9fSwiaWRlbnRpdHkiOnsiaW50ZXJuYWwiOnsiYXV0aF90aW1lIjoxNDAwLCJvcmdfaWQiOiIxMjM4MzAzMiJ9LCJhY2NvdW50X251bWJlciI6IjYyMTIzNzciLCJhdXRoX3R5cGUiOiJiYXNpYy1hdXRoIiwidXNlciI6eyJmaXJzdF9uYW1lIjoiSW5zaWdodHMiLCJpc19hY3RpdmUiOnRydWUsImlzX2ludGVybmFsIjpmYWxzZSwibGFzdF9uYW1lIjoiUUUiLCJsb2NhbGUiOiJlbl9VUyIsImlzX29yZ19hZG1pbiI6dHJ1ZSwidXNlcm5hbWUiOiJpbnNpZ2h0cy1xZSIsImVtYWlsIjoiam5lZWRsZStxYUByZWRoYXQuY29tIn0sInR5cGUiOiJVc2VyIn19", // (string)
  "timestamp": "2020-01-23T16:15:59.478901889Z" // (string)
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

### Processing

The ICM `Engine` class will take the downloaded tarball and, using **ccx-ocp-core** and **ccx-rules-ocp**, process it
and generates a JSON report. This report will be handled and sent to a configured Kafka topic using a `KafkaPublisher`.


### Reporting

The JSON report generated in the previous step will be sent to a Kafka topic where other services can take this record
and handle it properly. Generated JSON has format:

```
{
  "OrgID": 123456, // (int) - number that we get from b64_identity field
  "ClusterName": "aaaaaaaa-bbbb-cccc-dddd-000000000000", // (string) - cluster UUID  that we read from URL
  "Report": "{...}", // (string) - stringified JSON, that contains results of executing rules,
  "LastChecked": "2020-01-23T16:15:59.478901889Z" // (string) - time of the archive uploading in ISO 8601 format, gotten from "timestamp" field
}
```

### Prometheus statistics

The project allows to expose some metrics to **Prometheus** if desired. To enable it, you should add the
`ConsumerWatcher` to the configuration file, as shown in the [provided one](config.yaml)


The exposed metrics are 6 counters and 3 histograms:

- `ccx_consumer_received_total`: a counter of the total amount of received messages from Kafka that can be handled by
  the pipeline.
- `ccx_downloaded_total`: total amount of handled messages that contains a valid and downloadable archive.
- `ccx_engine_processed_total`: total amount of archives processed by the Insights library.
- `ccx_published_total`: total amount of processed results that has been published to the outgoing Kafka topic.
- `ccx_failures_total`: total amount of individual events received but not properly processed by the pipeline. It can
  include failures due to an invalid URL for the archive, incorrect format of the downloaded archive, failure during the
  processing...
- `ccx_not_handled_total`: total amount of received records that cannot be handled by the pipeline, normally due to
  incompatible format or incorrect JSON schema.
- `ccx_download_duration_seconds`: histogram of the time that takes to download each archive.
- `ccx_process_duration_seconds`: histogram of the time that takes to process the archive after it has been downloaded.
- `ccx_publish_duration_seconds`: histogram of the time that takes to send the new record to the outgoing Kafka topic
  after the archive has been processed.

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
  pipeline processing steps. The default configured one is `controller.consumer_watcher.ConsumerWatcher`
  that serve some statistics for [Prometehus service](https://prometheus.io/). The port where the
  `prometheus_client` library will listen for petitions is configurable using `kwargs` dictionary in the
  same way as `consumer` and `publisher`. The only recognized option is:
  - `prometheus_port`: an integer indicating the port where the `prometheus_client` will listen for server
    petitions. If not present, defaults to 8000.

## Deploy

ccx-data-pipeline runs in cloud.redhat.com and it's a part of the same testing and promoting routines. There are three
environments: CI, QA and PROD. The code should pass tests in QA env before it goes to PROD. cloud.redhat.com team
uses jenkins, OCP and [ocdeployer](https://github.com/bsquizz/ocdeployer) for code deploying. All deployment
configs are stored in [e2e-deploy](https://github.com/RedHatInsights/e2e-deploy) git repository.

## References
- [Promoting pipeline documentation](https://github.com/RedHatInsights/e2e-deploy/blob/master/docs/pipeline.md)
- ccx-data-pipeline namespaces:
  [ci](https://console.insights-dev.openshift.com/console/project/ccx-data-pipeline-ci/),
  [qa](https://console.insights-dev.openshift.com/console/project/ccx-data-pipeline-qa),
  [prod](https://console.insights.openshift.com/console/project/ccx-data-pipeline-prod)
- [Buildconfigs](https://github.com/RedHatInsights/e2e-deploy/tree/master/buildfactory/ccx-data-pipeline)
- [OCP templates](https://github.com/RedHatInsights/e2e-deploy/tree/master/templates/ccx-data-pipeline)
- [Jenkins](https://github.com/RedHatInsights/e2e-deploy/tree/master/templates/ccx-data-pipeline)
