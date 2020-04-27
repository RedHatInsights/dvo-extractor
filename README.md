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
2. Insights operator data is read from S3 Bucket and insights rules are applied to that data
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

The fields come from:

- `OrgID`: retrieved from the incoming JSON, codified inside the `b64_identity` value. It is extracted from
  `identity-internal-org_id` path of keys.
- `ClusterName`: the cluster name is retrieved from the downloaded archive. When the download successes and the archive
  is extracted prior to its processing by the engine, the cluster ID is read from a file named `config/id`.
- `Report`: is the JSON generated by the engine when the archive is processed.
- `LastChecked`: this field is copied directly from the incoming JSON, as `timestamp` key.

### Cluster name extraction internals

As the cluster ID is only present inside the archive and the set of rules to be executed is configurable, this pipeline
cannot relay on the executed rules to get the cluster name.

For that reason, a mixed `Watcher` was created: `ClusterIdWatcher`, that inherits from both `EngineWatcher` and
`ConsumerWatcher`. This double inheritance allows this watcher to receive notification from both entities of the
pipeline. The relevant events for this watcher are:

- `on_recv`: a consumer event used to store the `ConsumerRecord` object, needed to store the cluster name, when
  extracted
- `on_extract`: an engine event triggered when the archive is extracted, but not already processed. At this point, the
  files on the archive are available in the internal storage, so the relevant file can be read in order to store its
  content as cluster name.

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

The log format is highly configurable through the configuration file. By default, using the
[provided configuration](config.yaml), each log message will produce a JSON dictionary with the following structure:

```json5
{
  "levelname": "LOG_LEVEL",
  "asctime": "timestamp",
  "name": "Python module",
  "filename": "filename",
  "message": "Message content"
}
```

By default, this log messages will be printed in the standard output. To change this behaviour, refer to the `logging`
section in the [configuration file](config.yaml),  the
[Python Logging HOWTO](https://docs.python.org/3.6/howto/logging.html#configuring-logging) and the
[Python logging reference](https://docs.python.org/3.6/library/logging.config.html#module-logging.config)

## Implementation

To be described

## Local setup

There is a `docker-compose` configuration that provisions a minimal stack of Insight Platform and
a postgres database.
You can download it here https://gitlab.cee.redhat.com/insights-qe/iqe-ccx-plugin/blob/master/docker-compose.yml

### Prerequisites

* minio requires `../minio/data/` and `../minio/config` directories to be created
* edit localhost line in your `/etc/hosts`:  `127.0.0.1       localhost kafka minio`
* `ingress` image should present on your machine. You can build it locally from this repo https://github.com/RedHatInsights/insights-ingress-go

### Usage

1. Start the stack `podman-compose up` or `docker-compose up`
2. Wait until kafka will be up.
3. Start `ccx-data-pipeline`: `python3 -m insights_messaging config-devel.yaml`

Stop Minimal Insights Platform stack `podman-compose down` or `docker-compose down`

In order to upload an insights archive, you can use `curl`:
```
curl -k -vvvv -F "upload=@/path/to/your/archive.zip;type=application/vnd.redhat.testareno.archive+zip" http://localhost:3000/api/ingress/v1/upload -H "x-rh-identity: eyJpZGVudGl0eSI6IHsiYWNjb3VudF9udW1iZXIiOiAiMDAwMDAwMSIsICJpbnRlcm5hbCI6IHsib3JnX2lkIjogIjEifX19Cg=="
```

or you can use integration tests suite. More details are [here](https://gitlab.cee.redhat.com/insights-qe/iqe-ccx-plugin).

## Logstash configuration

Clone this repo https://github.com/deviantony/docker-elk and start `docker-compose up` in it's directory.
Don't forget to use the latest docker version(fedora repository doesn't have the latest version).


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
  - `group_id`: Kafka group identifier. Several instances of the same pipeline will need to be into
    the same group in order to not process the same messages.
  - `bootstrap_servers`: a list of "IP:PORT" strings where the Kafka server is listening.
- `publisher` name refers to the class `controller.publisher.Publisher` and it also allow to define the
  arguments passed to the initializer modifying the `kwargs` dictionary:
  - `outgoing_topic`: a string indicating the topic where the reported results should be sent.
  - `bootstrap_servers`: same as in `consumer`, a list of Kafka servers to connect
- `watchers`: it has a list of `Watcher` objects that will receive notifications of events during the
  pipeline processing steps. The default configured one is `controller.consumer_watcher.ConsumerWatcher`
  that serve some statistics for [Prometheus service](https://prometheus.io/). The port where the
  `prometheus_client` library will listen for petitions is configurable using `kwargs` dictionary in the
  same way as `consumer` and `publisher`. The only recognized option is:
  - `prometheus_port`: an integer indicating the port where the `prometheus_client` will listen for server
    petitions. If not present, defaults to 8000.

## Environment variables

In addition to the configuration mentioned in the previous section, some other behaviours can be configured
through the definition of environment variables.

All the YAML file is parsed by the Insights Core Messaging library, that includes support for using
environment variables with default values as values for any variable in the configuration file.

As an example, given an environment variable named `CDP_INCOMING_TOPIC` that contains the Kafka topic name
where the consumer should read, you can put `${CDP_INCOMING_TOPIC}` as the value for the
`consumer`/`incoming_topic` configuration.

Following the same example, if you want that a default value is used in case of `CDP_INCOMING_TOPIC` is not
defined, you can specify `${CDP_INCOMING_TOPIC:default_value}`. In this case, the environment variable will
take precedence over the default value, but this default will be used in case the environment variable is
not defined.

In addition to the YAML configuration, another important note about the needed environment variables:

### Cloud Watch configuration

Cloud Watch is a service to enable log message publication. In `ccx-data-pipeline` it is done using `boto3` and
`watchtower` Python packages.

To enable the sending of log messages to a Cloud Watch instance, you should define **all** the following
environment variables:

- `CW_AWS_ACCESS_KEY_ID`: The AWS access key for creating the Cloud Watch session.
- `CW_AWS_SECRET_ACCESS_KEY`: The AWS secret access key for creating the Cloud Watch session.
- `AWS_REGION_NAME:`: An AWS region name where the Cloud Watch authentication should be done.
- `CW_LOG_GROUP`: The logging group that will be used by `ccx-data-pipeline` to publish its messages.
- `CW_STREAM_NAME`: A name to distinguish this application logs inside the log group.

If any of these environment variables are not defined, the Cloud Watch service cannot be configured and
won't be used at all.

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
