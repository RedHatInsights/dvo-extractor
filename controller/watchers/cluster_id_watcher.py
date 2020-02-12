"""Module including a mixed watcher to retrieve the cluster ID from the extracted file."""

import os

from insights_messaging.watchers import ConsumerWatcher, EngineWatcher


class ClusterIdWatcher(EngineWatcher, ConsumerWatcher):
    """Mixed `Watcher` that is able to watch both `Consumer` and `Engine`."""

    def __init__(self):
        """Initialize a `ClusterIdWatcher`."""
        self.last_record = None

    def on_recv(self, input_msg):
        """Get and stores the `ConsumerRecord` when a new Kafka record arrives."""
        self.last_record = input_msg

    def on_extract(self, ctx, broker, extraction):
        """Receive the notification when the file is extracted.

        The method get the directory where the files are extracted and find the
        id in the expected path.
        """
        id_file_path = os.path.join(ctx.root, 'config', 'id')
        with open(id_file_path, 'r') as id_file:
            self.last_record.value["ClusterName"] = id_file.read()
