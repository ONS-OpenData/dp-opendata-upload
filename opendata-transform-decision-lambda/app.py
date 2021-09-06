import json
import os
from pathlib import Path
import logging

import boto3

# When we build the container the imports from ../common will be exist locally to the function.
# This catch is just to enable intellisense while developing.
try:
    from ..common.helpers import (
        log_as_incomplete,
        log_as_complete,
        TransformType,
        json_validate,
    )
    from ..common.mocking import MockClient
    from ..common.schemas import (
        bucket_notification_event_schema,
        transform_details_schema,
        decision_lambda_source_schema,
        short_transform_evocation_payload_schema,
    )
except ImportError:
    from helpers import log_as_incomplete, log_as_complete, TransformType, json_validate
    from mocking import MockClient
    from schemas import (
        bucket_notification_event_schema,
        transform_details_schema,
        decision_lambda_source_schema,
        short_transform_evocation_payload_schema,
    )

# When testing, use the mocked lambda client
if os.environ.get("IS_TEST", None):
    client = MockClient()
else:
    client = client = boto3.client("lambda")


def handler(event, context):
    """
    Principle lambda event handler.
    """

    json_validate(event, bucket_notification_event_schema)
    record = event.get("Records")[0]
    bucket = record["s3"]["bucket"]["name"]
    zip_file = record["s3"]["object"]["key"]

    source_dict = {"bucket": bucket, "zip_file": zip_file}
    json_validate(source_dict, decision_lambda_source_schema)

    r = client.invoke(
        FunctionName="opendata-transform-details-lambda",
        InvocationType="RequestResponse",
        Payload=json.dumps(source_dict),
    )

    payload_dict = json.load(r["Payload"])
    if payload_dict["statusCode"] != 200:
        log_as_incomplete()
        raise Exception(
            f"Failed to get response from opendata-transform-details-lambda, with status code {payload_dict['statusCode']}"
        )
    payload_body = json.loads(payload_dict["body"])
    transform_details = payload_body.get("transform_details")
    json_validate(transform_details, transform_details_schema)
    transform_type = transform_details.get("transform_type")

    if transform_type == TransformType.long.value:
        log_as_incomplete()
        raise NotImplementedError("Not looking at long running transforms yet.")

    elif transform_type == TransformType.none.value:
        log_as_incomplete()
        raise NotImplementedError(
            "Not looking at sources that dont need transforms yet."
        )

    elif transform_type == TransformType.short.value:
        transform_details["source"] = source_dict
        del transform_details["transform_type"]  # no longer needed
        json_validate(transform_details, short_transform_evocation_payload_schema)

        client.invoke(
            FunctionName="opendata-transformer-lambda",
            InvocationType="Event",
            Payload=json.dumps(transform_details),
        )
        log_as_complete()

    else:
        log_as_incomplete()
        raise ValueError(
            f"Unknown transform type {transform_type}. Should be one of {TransformType.values()}"
        )
