---
layout: page
nav_order: 7
---
# Environment variables

In addition to the configuration mentioned in the previous section, some other
behaviours can be configured through the definition of environment variables.

All the YAML file is parsed by the Insights Core Messaging library, that
includes support for using environment variables with default values as values
for any variable in the configuration file.

As an example, given an environment variable named `CDP_INCOMING_TOPIC` that
contains the Kafka topic name where the consumer should read, you can put
`${CDP_INCOMING_TOPIC}` as the value for the `consumer`/`incoming_topic`
configuration.

Following the same example, if you want that a default value is used in case of
`CDP_INCOMING_TOPIC` is not defined, you can specify
`${CDP_INCOMING_TOPIC:default_value}`. In this case, the environment variable
will take precedence over the default value, but this default will be used in
case the environment variable is not defined.

In addition to the YAML configuration, another important note about the needed
environment variables:

## Cloud Watch configuration

Cloud Watch is a service to enable log message publication. In
`ccx-data-pipeline` it is done using `boto3` and `watchtower` Python packages.

To enable the sending of log messages to a Cloud Watch instance, you should
define **all** the following environment variables:

- `CW_AWS_ACCESS_KEY_ID`: The AWS access key for creating the Cloud Watch
  session.
- `CW_AWS_SECRET_ACCESS_KEY`: The AWS secret access key for creating the Cloud
  Watch session.
- `AWS_REGION_NAME:`: An AWS region name where the Cloud Watch authentication
  should be done.
- `CW_LOG_GROUP`: The logging group that will be used by `ccx-data-pipeline` to
  publish its messages.
- `CW_STREAM_NAME`: A name to distinguish this application logs inside the log
  group.

If any of these environment variables are not defined, the Cloud Watch service
cannot be configured and won't be used at all.
