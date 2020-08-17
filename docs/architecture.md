---
layout: page
nav_order: 1
---
# Architecture

This service is built on top of [insights-core-messaging
framework](https://github.com/RedHatInsights/insights-core-messaging) and will
be deployed and run inside [cloud.redhat.com](https://cloud.redhat.com).

## External data pipeline diagram

![diagram](./external_pipeline_diagram.jpg)

## Sequence diagram

![sequence](./sequence-diagram.png)

## Whole data flow

![data_flow](./customer_facing_services_architecture.png)

1. Event about new data from insights operator is consumed from Kafka. That event contains (among other things) URL to S3 Bucket
2. Insights operator data is read from S3 Bucket and insights rules are applied to that data
3. Results (basically organization ID + cluster name + insights results JSON) are stored back into Kafka, but into different topic
4. That results are consumed by Insights rules aggregator service that caches them
5. The service provides such data via REST API to other tools, like OpenShift Cluster Manager web UI, OpenShift console, etc.

