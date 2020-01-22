# CCX Data Pipeline

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

This service will receive records from a given Kafka topic, download the items from the S3 server
and send them to **insights-ocp**.

After being parsed, the results will be notified through a different Kafka topic and logged in a
way to be determined.

![diagram](./doc/external_pipeline_diagram.jpg)

This service is built on top of [insights-core-messaging framework](https://github.com/RedHatInsights/insights-core-messaging)
and will be deployed and run inside https://cloud.redhat.com

## Sequence diagram

![sequence](./doc/sequence-diagram.png)

## Data consumer

Every time a new record is sent by Kafka to the subscribes topic, the `KafkaConsumer` will handle and process it,
recovering from the corresponding S3 bucket, and passing the downloaded file to the processor module.

## Processor module

TBD

## Reporting

**insights-ocp** processes the tarball downloaded from S3 bucket and generates
a JSON report.  This report will be handled and sent to a Kafka topic
**platform.results.ccx**, where other services can take this record and handle
it properly.

### Format of the notified Kafka records

TBD

### Format of the logs

TBD

## Implementation

To be described

## Usage

First you need to start Kafka, through `docker-compose`:

```Shell
docker-compose up -d
```

Second step is to install python dependencies:

```Shell
pip install -e .
```

Third step is to start controller:

```Shell
python -u -m insights_messaging config.yaml
```
