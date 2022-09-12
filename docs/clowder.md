# Clowder configuration

As the rest of the services deployed in the Console RedHat platform, the
CCX Data Pipeline Archives Handler should update its configuration using
the relevant values extracted from the Clowder configuration file.

For a general overview about Clowder configuration file and how it is used
in the external data pipeline, please refer to
[Clowder configuration](https://ccx.pages.redhat.com/ccx-docs/customer/clowder.html)
in CCX Docs.

## How can we deal with the Clowder configuration file?

As the service is implemented in Python, we take advantage of using
[app-common-python](https://github.com/RedHatInsights/app-common-python/).
It provides to the service all the needed values for configuring Kafka
access and the topics name mapping.

To accomplish the task of mixing together both configuration inputs and
apply the resulting one, the hard work is done in our
`ccx_messaging.utils.clowder`.

# CCX Data Pipeline specific relevant values

For this service, the relevant values are referred to be the Kafka access
parameters and the Kafka topics name mapping.

The entities that should be configured with the injected values are the
consumer, publisher and, if configured to use them, Payload Tracker Watcher
and Dead Letter Queue publisher.
