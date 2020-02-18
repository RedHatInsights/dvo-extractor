"""Module including a mixed watcher to retrieve the cluster ID from the extracted file."""

import logging
import os
from uuid import UUID

from insights_messaging.watchers import ConsumerWatcher, EngineWatcher


log = logging.getLogger(__name__)


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
        if self.last_record is None:
            log.warning("Unexpected data flow: watched extraction event without "
                        "a previous receiving event")
            return

        id_file_path = os.path.join(ctx.root, 'config', 'id')

        try:
            with open(id_file_path, 'r') as id_file:
                cluster_uuid = id_file.read()

                try:
                    UUID(cluster_uuid)
                    self.last_record.value["ClusterName"] = cluster_uuid

                except ValueError:
                    self.last_record.value["ClusterName"] = None
                    log.warning("The cluster id is not an UUID. Skipping its extraction")

        except FileNotFoundError:
            self.last_record.value["ClusterName"] = None
            log.warning(
                "The archive doesn't contain a valid Cluster Id file. Skipping its extraction")

        finally:
            self.last_record = None
