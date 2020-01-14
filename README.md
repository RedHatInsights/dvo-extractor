# CCX Data Pipeline

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

This service will receive records from a given Kafka topic, download the items from the S3 server
and send them to **insights-ocp**.

After being parsed, the results will be notified thorugh a different Kafka topic and logged in a
way to be determined.

![diagram](./doc/external_pipeline_diagram.jpg)

This service will be built in top of [insights-core-messaging framework](https://github.com/RedHatInsights/insights-core-messaging)
and will be deployed and run inside https://cloud.redhat.com

## Data consumer

Every time a new record is sent by Kafka to the subscribes topic, the `KafkaConsumer` will handle and process it,
recovering from the corresponding S3 bucket, and passing the downloaded file to the processor module.

## Processor module

TBD

## Reporting

After **insights-ocp** processes the file, a JSON report will be received. This report will be handle and sent,
in first place, to a different Kafka topic, where other services can take this record hand handle it properly.

In addition, some logs will be generated.

### Format of the notified Kafka records

TBD

### Format of the logs

TBD

