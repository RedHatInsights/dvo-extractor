"""Module containing JSON schemas used by this application."""

# Schema of the input message consumed from Kafka.
INPUT_MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {"type": "string"}
    },
    "required": ["url"]
}
