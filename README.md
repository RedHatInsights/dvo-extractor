# CCX Data Pipeline

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

This service will receive records from a given Kafka topic, download the items
from the S3 server and apply Insights rules to downloaded tarball.

JSON containing Insights rules results will be send to a different Kafka topic
and logged in a way to be determined.

Incoming and outgoing Kafka topics are configurable, these can be even handled
by different Kafka instances.

![diagram](./doc/external_pipeline_diagram.jpg)

This service is built on top of [insights-core-messaging framework](https://github.com/RedHatInsights/insights-core-messaging)
and will be deployed and run inside [cloud.redhat.com](https://cloud.redhat.com).

## Sequence diagram

![sequence](./doc/sequence-diagram.png)

## Data consumer

Every time a new record is sent by Kafka to the subscribes topic, the `KafkaConsumer` will handle and process it,
recovering from the corresponding S3 bucket, and passing the downloaded file to the processor module.

## Processor module

TBD

## Reporting

**ccx-ocp-core** and **ccx-rules-ocp** process the tarball downloaded from S3
bucket and generates a JSON report. This report will be handled and sent to a
configured Kafka topic where other services can take this record and handle it
properly.

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

