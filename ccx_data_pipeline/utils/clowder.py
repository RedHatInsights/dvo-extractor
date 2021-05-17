import yaml
from app_common_python import LoadedConfig


def apply_clowder_config(manifest):
    """Applies Clowder config values to ICM config manifest"""
    Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    config = yaml.load(manifest, Loader=Loader)
    kafka_url = f"{LoadedConfig.kafka.brokers[0].hostname}:{LoadedConfig.kafka.brokers[0].port}"
    config["service"]["consumer"]["kwargs"]["bootstrap_servers"] = kafka_url
    config["service"]["publisher"]["kwargs"]["bootstrap_servers"] = kafka_url
    pt_watcher = "ccx_data_pipeline.watchers.payload_tracker_watcher.PayloadTrackerWatcher"
    for watcher in config["service"]["watchers"]:
        if watcher["name"] == pt_watcher:
            watcher["kwargs"]["bootstrap_servers"] = kafka_url
    return config
