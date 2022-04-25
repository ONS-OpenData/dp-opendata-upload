# Note: we start with two huge schemas for the AWS bucket notificatons.
# one for zip appearing in source bucket.
# one for v4 appearing in v4 upload bucket.
# the only difference is the file extension they check for in the key.


# The event triggered by our initial zip file entering the source bucket
# Used by the transform_decision_lambda
transform_decision_event_schema = {
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
# Used by the transform details lambda, is the same as metadata_validator_schema
transform_details_event_schema = {
    "properties": {
        "bucket": {"type": "string"},
        "zip_file": {"type": "string", "pattern": "zip$"},
        "request_id": {"type": "string"},
    },
    "required": ["bucket", "zip_file", "request_id"],
}

# The payload received back from opendata-transform-details-lambda
transform_details_response_schema = {
    "properties": {
        "statusCode": {"type": "integer"},
        "body": {
            "type": "object",
            "properties": {
                "transform_details": {
                    "type": "object",
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
                },
            },
        "required": ["transform_details"],       
    },
    "request_id": {"type": "string"},
    },
    "required": [
        "statusCode",
        "body",
        "request_id"
            ],
}

# A dict to allow access to the original zip in the source bucket
# Used by the metadata validator lambda, is the same as transform_details_schema
metadata_validator_event_schema = {
    "properties": {
        "bucket": {"type": "string"},
        "zip_file": {"type": "string", "pattern": "zip$"},
        "request_id": {"type": "string"},
    },
    "required": ["bucket", "zip_file", "request_id"],
}

# The response from the metadata validator
metadata_validator_response_schema = {
    "properties": {
        "statusCode": {"type": "integer"},
        "body": {
            "type": "object",
            "properties": {
                "valid": {"type": "boolean"}
            },
            "required": ["valid"],
        "request_id": {"type": "string"},
        },
    },
    "required": ["statusCode", "body", "request_id"],
}



# The payload sent to initialise the transform or skip transform) process
source_extractor_event_schema = {
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
            },
        },
        "request_id": {"type": "string"},
    },
    "required": [
        "transform",
        "dataset_id",
        "edition_id",
        "collection_name",
        "source",
        "request_id",
    ],
}

# The payload sent to initialise the transformer lambda
# same as source extractor
transformer_event_schema = {
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
            },
        },
        "request_id": {"type": "string"},
    },
    "required": [
        "transform",
        "dataset_id",
        "edition_id",
        "collection_name",
        "source",
        "request_id",
    ],
}

# The payload sent to initialise the transform retriever
transform_retriever_event_schema = {
    "properties": {
        "transform": {"type": "string"},
        "request_id": {"type": "string"},
    },
    "required": ["transform", "request_id"],
}

# The response from the transform retriever
transform_retriever_response_schema = {
    "properties": {
        "statusCode": {"type": "integer"},
        "body": {"type": "string"},
        "requirements": {"type": "object"},
        "request_id": {"type": "string"},
    },
    "required": ["statusCode", "body", "request_id"],
}

# The payload sent to initialise the upload process
upload_initialiser_event_schema = {
    "properties": {
        "dataset_id": {"type": "string"},
        "edition_id": {"type": "string"},
        "collection_name": {"type": "string"},
        "source": {
            "type": "object",
            "properties": {
                "bucket": {"type": "string"},
                "zip_file": {"type": "string", "pattern": "zip$"},
            },
        },
        "s3_url": {"type": "string"},
        "request_id": {"type": "string"},
    },
    "required": [
        "dataset_id",
        "edition_id",
        "collection_name",
        "source",
        "s3_url",
        "request_id",
    ],
}

upload_metadata_parser_event_schema = {
    "properties": {
        "bucket": {"type": "string"},
        "zip_file": {"type": "string", "pattern": "zip$"},
        "request_id": {"type": "string"},
    },
    "required": ["bucket", "zip_file", "request_id"],
}

upload_metadata_parser_response_schema = {
    "properties": {
        "statusCode": {"type": "integer"},
        "body": {
            "type": "object",
            "properties": {
                "metadata": {"type": "object"},
                "dimension_data": {"type": "object"},
                "usage_notes": {"type": "array"}
            },
            "required": [
                "metadata",
                "dimension_data",
                "usage_notes",
            ],
        },
        "request_id": {"type": "string"}
    },
    "required": [
        "statusCode",
        "body",
        "request_id",
    ],
}

upload_poller_event_schema = {
    "properties": {
        "instance_id": {"type": "string"},
        "metadata_dict": {
            "type": "object",
            "properties": {
                "metadata": {"type": "object"},
                "dimension_data": {"type": "object"},
                "usage_notes": {"type": "array"},
            },
            "required": [
                "metadata", 
                "dimension_data", 
                "usage_notes"
                ],
        },
        "dataset_details": {
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string"},
                "edition_id": {"type": "string"},
                "collection_name": {"type": "string"},
            },
            "required": [
                "dataset_id",
                "edition_id",
                "collection_name",
            ],
        },
        "count": {"type": "integer"},
        "request_id": {"type": "string"},
    },
    "required": [
        "instance_id", 
        "metadata_dict", 
        "dataset_details",
        "count",
        "request_id",
        ],
}

upload_finaliser_event_schema = {
    "properties": {
        "instance_id": {"type": "string"},
        "metadata_dict": {
            "type": "object",
            "properties": {
                "metadata": {"type": "object"},
                "dimension_data": {"type": "object"},
                "usage_notes": {"type": "array"},
            },
            "required": [
                "metadata", 
                "dimension_data", 
                "usage_notes"
                ],
        },
        "dataset_details": {
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string"},
                "edition_id": {"type": "string"},
                "collection_name": {"type": "string"},
            },
            "required": [
                "dataset_id",
                "edition_id",
                "collection_name",
            ],
        },
        "request_id": {"type": "string"},
    },
    "required": [
        "instance_id", 
        "metadata_dict", 
        "dataset_details",
        "request_id",
        ],
}

# Dict with the required metadata to upload a v4
valid_metadata_schema = {
    "properties": {
        "metadata": {"type": "object"},
        "dimension_data": {"type": "object"},
        "usage_notes": {"type": "array"},
    },
    "required": ["metadata", "dimension_data", "usage_notes"],
}

# Dict of metadata created from CMD
# currently bare bones of schema
cmd_metadata_schema = {
    "properties": {
        "@context": {"type": "string"},
        "dct:issued": {"type": "string"},
        "dct:title": {"type": "string"},
        "tableSchema": {"type": "object"},
        "url": {"type": "string"},
    },
    "required": ["@context", "dct:issued", "dct:title", "tableSchema", "url"]
}

manifest_schema = {
    "properties": {
        "metadata": {"type": "string"},
        "metadata_handler": {"type": "string"},
    },
    "required": ["metadata", "metadata_handler"],
}

