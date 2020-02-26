"""Module containing JSON schemas used by this application."""

# Schema of the input message consumed from Kafka.
INPUT_MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {"type": "string"},
        "b64_identity": {
            "type": "string",
            "contentEncoding": "base64",
        },
        "timestamp": {"type": "string"}
    },
    "required": ["url", "b64_identity", "timestamp"]
}

IDENTITY_SCHEMA = {
    "type": "object",
    "properties": {
        "identity": {
            "type": "object",
            "properties": {
                "account_number": {"type": "string"},
                "auth_type": {"type": "string"},
                "internal": {
                    "type": "object",
                    "properties": {
                        "auth_time": {"type": "integer"},
                        "org_id": {"type": "string"},
                    },
                    "required": ["org_id"],
                },
                "type": {"type": "string"},  # type is a property of the identity
                "user": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "first_name": {"type": "string"},
                        "is_active": {"type": "boolean"},
                        "is_internal": {"type": "boolean"},
                        "is_org_admin": {"type": "boolean"},
                        "last_name": {"type": "string"},
                        "locale": {"type": "string"},
                        "username": {"type": "string"},
                    },
                },
            },
        },
    },
}
