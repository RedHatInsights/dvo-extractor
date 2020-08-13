---
layout: page
nav_order: 6
---
# Configuration

The `config.yaml` is an standard **Insights Core Messaging** configuration file.
To learn about its structure and configuring some common things, you probably
want to read its documentation:

[Insights Core Messaging
documentation](https://github.com/RedHatInsights/insights-core-messaging#example-configuration).

Some of the specific **ccx-data-pipeline** configuration points are in the
`service` section, where the specific _consumer_, _downloader_ and _publisher_
are configured.

- `consumer` name refers to the class `ccx_data_pipeline.consumer.Consumer`. The
  arguments passed to the initializer are defined in the `kwargs` dictionary
  initializer. The most relevants are:
  - `incoming_topic`: the Kafka topic to subscribe the consumer object.
  - `group_id`: Kafka group identifier. Several instances of the same pipeline
    will need to be into the same group in order to not process the same
    messages.
  - `bootstrap_servers`: a list of "IP:PORT" strings where the Kafka server is
    listening.
  - `max_record_age`: an integer that defines the amount of seconds for ignoring
    older Kafka records. If a received record is older than this amount of
    seconds, it will be ignored. By default, messages older than 2 hours will be
    ignored. To disable this functionality and process every record ignoring its
    age, use `-1`.
- `downloader`: name refers to the class
  `ccx_data_pipeline.http_downloader.HTTPDownloader`. The only argument that can
  be passed to the initializer is:
  - `max_archive_size`: this is an optional argument. It will specify the
    maximum size of the archives that can be processed by the pipeline. If the
    downloaded archive is bigger, it will be discarded. The parameter should be
    an string in a human-readable format (it accepts units like KB, KiB, GB,
    GiB...
- `publisher` name refers to the class `ccx_data_pipeline.publisher.Publisher`
  and it also allow to define the arguments passed to the initializer modifying
  the `kwargs` dictionary:
  - `outgoing_topic`: a string indicating the topic where the reported results
    should be sent.
  - `bootstrap_servers`: same as in `consumer`, a list of Kafka servers to
    connect
- `watchers`: it has a list of `Watcher` objects that will receive notifications
  of events during the
  pipeline processing steps. The default configured one is
  `ccx_data_pipeline.consumer_watcher.ConsumerWatcher` that serve some
  statistics for [Prometheus service](https://prometheus.io/). The port where
  the `prometheus_client` library will listen for petitions is configurable
  using `kwargs` dictionary in the same way as `consumer` and `publisher`. The
  only recognized option is:
  - `prometheus_port`: an integer indicating the port where the
    `prometheus_client` will listen for server petitions. If not present,
    defaults to 8000.
