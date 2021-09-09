from distutils.util import strtobool
import json
import logging
import os

import boto3

# When we build the container the imports from ../common will be exist locally to the function.
# This catch is just to enable intellisense while developing.
# When we're closer to done, the contents of /common will be a pip installable package so
# this nasty catch can go.
try:
    from ..common.helpers import (
        log_as_incomplete,
        log_as_complete,
        json_validate,
        dataset_name_from_zip_name,
    )
    from ..common.mocking import get_lambda_client
    from ..common.schemas import source_bucket_schema, transform_details_schema
except ImportError:
    from helpers import (
        log_as_incomplete,
        log_as_complete,
        json_validate,
        dataset_name_from_zip_name,
    )
    from mocking import get_lambda_client
    from schemas import source_bucket_schema, transform_details_schema


def handler(event, context):

    client = get_lambda_client()

    json_validate(event, source_bucket_schema)

    zip_file = event.get("zip_file")
    dataset_name = dataset_name_from_zip_name(zip_file)

    # Get transform details from details.json
    with open("details.json") as f:
        data = json.load(f)
    transform_details_dict = data.get(dataset_name)
    json_validate(transform_details_dict, transform_details_schema)

    r = client.invoke(
        FunctionName="opendata-metadata-validator",
        InvocationType="RequestResponse",
        Payload=json.dumps(event),
    )

    payload_dict = json.load(r["Payload"])
    if payload_dict["statusCode"] != 200:
        log_as_incomplete()
        raise Exception(
            f"Failed to get response from opendata-metadata-validator, with status code {payload_dict['statusCode']}"
        )

    is_valid = strtobool(json.loads(payload_dict["body"])["valid"])
    if not is_valid:
        log_as_incomplete()
        raise Exception("Aborting for invalid metadata.")

    log_as_complete()
    return {
        "statusCode": 200,
        "body": json.dumps({"transform_details": transform_details_dict}),
    }
