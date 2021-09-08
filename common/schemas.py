# The event triggered by our initial xip file entering the bucket
bucket_notification_event_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "properties": {
        "Records": {
            "type": "array",
            "items": [
                {
                    "type": "object",
                    "properties": {
                        "eventVersion": {"type": "string"},
                        "eventSource": {"type": "string"},
                        "awsRegion": {"type": "string"},
                        "eventTime": {"type": "string"},
                        "eventName": {"type": "string"},
                        "userIdentity": {
                            "type": "object",
                            "properties": {"principalId": {"type": "string"}},
                            "required": ["principalId"],
                        },
                        "requestParameters": {
                            "type": "object",
                            "properties": {"sourceIPAddress": {"type": "string"}},
                            "required": ["sourceIPAddress"],
                        },
                        "responseElements": {
                            "type": "object",
                            "properties": {
                                "x-amz-request-id": {"type": "string"},
                                "x-amz-id-2": {"type": "string"},
                            },
                            "required": ["x-amz-request-id", "x-amz-id-2"],
                        },
                        "s3": {
                            "type": "object",
                            "properties": {
                                "s3SchemaVersion": {"type": "string"},
                                "configurationId": {"type": "string"},
                                "bucket": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "ownerIdentity": {
                                            "type": "object",
                                            "properties": {
                                                "principalId": {"type": "string"}
                                            },
                                            "required": ["principalId"],
                                        },
                                        "arn": {"type": "string"},
                                    },
                                    "required": ["name", "ownerIdentity", "arn"],
                                },
                                "object": {
                                    "type": "object",
                                    "properties": {
                                        "key": {"type": "string", "pattern": "zip$"},
                                        "size": {"type": "integer"},
                                        "eTag": {"type": "string"},
                                        "sequencer": {"type": "string"},
                                    },
                                    "required": ["key", "size", "eTag", "sequencer"],
                                },
                            },
                            "required": [
                                "s3SchemaVersion",
                                "configurationId",
                                "bucket",
                                "object",
                            ],
                        },
                    },
                    "required": [
                        "eventVersion",
                        "eventSource",
                        "awsRegion",
                        "eventTime",
                        "eventName",
                        "userIdentity",
                        "requestParameters",
                        "responseElements",
                        "s3",
                    ],
                }
            ],
        }
    },
    "required": ["Records"],
}

# A dict to allow access to the original zip in the source bucket
source_bucket_schema = {
    "properties": {
        "bucket": {"type": "string"},
        "zip_file": {"type": "string", "pattern": "zip$"},
    },
    "required": ["bucket", "zip_file"],
}

# The payload received back from opendata-transform-details-lambda
transform_details_schema = {
    "properties": {
        "transform": {"type": "string"},
        "transform_type": {"type": "string", "pattern": "none|short|long"},
        "dataset_id": {"type": "string"},
        "edition_id": {"type": "string"},
        "collection_name": {"type": "string"},
    },
    "required": [
        "transform",
        "transform_type",
        "dataset_id",
        "edition_id",
        "collection_name",
    ],
}

# The payload sent to initialise the transform or skip transform) process
transform_evocation_payload_schema = {
    "properties": {
        "transform": {"type": "string"},
        "dataset_id": {"type": "string"},
        "edition_id": {"type": "string"},
        "collection_name": {"type": "string"},
        "source": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string"},
                "zip_file": {"type": "string", "pattern": "zip$"},
            }
        }
    },
    "required": [
        "transform",
        "dataset_id",
        "edition_id",
        "collection_name",
        "source",
    ],
}

# TODO - more details
# Dict with the required metadata to upload a v4
valid_metadata_schema = {
    "properties": {
        "metadata": {"type": "object"},
        "dimension_data": {"type": "object"},
        "usage_notes": {"type": "object"},
    },
    "required": ["metadata", "dimension_data", "usage_notes"],
}
