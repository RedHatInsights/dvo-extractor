# Logging

The log format is highly configurable through the configuration file.
In the running configuration, each log message has the following format:

```json
{
  "levelname": "LOG_LEVEL",
  "asctime": "timestamp",
  "name": "Python module",
  "filename": "filename",
  "message": "Message content"
}
```

By default, this log messages will be printed in the standard output.
To change this behaviour, refer to the `logging` section in the [configuration file][2],
the [Python Logging HOWTO][3] and the [Python logging reference][4].

To change the behaviour in the deployed instances, you should upgrade the `ConfigMap` section
in the [Clowder configuration file][5].

## Logging to Cloud Watch

Cloud Watch is a service to enable log message publication.
In `ccx-data-pipeline` it is done using `boto3` and `watchtower` Python packages.

In addition to the whole Python logging facilities, this service includes some
additional tooling in order to help configuring the logging system to send its
messages to a **Cloud Watch** instance.

Please, refer to [Cloud Watch configuration](configuration#cloudwatch-configuration)
section to get further info.

[1]: https://ccx.pages.redhat.com/ccx-docs/docs/processing/customer/monitoring/#logs
[2]: https://gitlab.cee.redhat.com/ccx/ccx-data-pipeline/-/blob/master/config.yaml
[3]: https://docs.python.org/3.6/howto/logging.html#configuring-logging
[4]: https://docs.python.org/3.6/library/logging.config.html#module-logging.config
[5]: https://gitlab.cee.redhat.com/ccx/ccx-data-pipeline/-/blob/master/deploy/clowdapp.yaml