from distutils.util import strtobool
import json
from pathlib import Path
import os

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    json_validate,
    dataset_name_from_zip_name,
)
from lambdautils.mocking import get_lambda_client
from lambdautils.schemas import transform_details_event_schema, metadata_validator_response_schema

import logging

this_dir = Path(os.path.dirname(os.path.realpath(__file__)))


def handler(event, context):
    """
    Triggered by opendata-transform-decision-lambda
    Gets transform details from details.json
    Invokes opendata-metadata-validator
    Returns transform_details
    """

    json_validate(event, transform_details_event_schema) 

    client = get_lambda_client()

    zip_file = event["zip_file"]
    dataset_name = dataset_name_from_zip_name(zip_file)

    # validate metadata by calling the metadata validator
    r = client.invoke(
        FunctionName="opendata-metadata-validator",
        InvocationType="RequestResponse",
        Payload=json.dumps(event),
    )

    payload_dict = json.load(r["Payload"])
    json_validate(payload_dict, metadata_validator_response_schema)
    if payload_dict["statusCode"] != 200:
        log_as_incomplete()
        raise Exception(
            f"Failed to get response from opendata-metadata-validator, with status code {payload_dict['statusCode']}"
        )

    is_valid = payload_dict["body"]["valid"]
    if not is_valid:
        log_as_incomplete()
        raise Exception("Aborting for invalid metadata.")    
    
    # Get transform details from details.json
    with open(Path(this_dir / "details.json")) as f:
        data = json.load(f)

    transform_details_dict = data[dataset_name]

    log_as_complete()
    return {
        "statusCode": 200,
        "body": {"transform_details": transform_details_dict},
        "request_id": event["request_id"]
    }
