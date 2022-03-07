import json
import logging
import requests
import os


from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    json_validate,
    Source,
    MetadataHandler,
    COMMON_ZIP_PATH
)

from lambdautils.mocking import get_s3_client
from lambdautils.schemas import source_bucket_schema, valid_metadata_schema


def handler(event, context):
    """
    Triggered by opendata-transform-details-lambda
    Gets the name of metadata file and metadata structure from manifest.json 
    Determins if metadata in source is in a valid format
    Returns {valid:True/False} 
    """

    s3 = get_s3_client()

    json_validate(event, source_bucket_schema)

    if isinstance(event, str):
        event = json.loads(event)
    bucket = event["bucket"]
    zip_file = event["zip_file"]

    with open(COMMON_ZIP_PATH, "wb") as f:
        s3.download_fileobj(bucket, zip_file, f)

    source = Source(COMMON_ZIP_PATH)
    metadata_handler = source.get_metadata_handler()

    # The correctly_structured handler is for where the metadata json should already
    # be in the shape we want
    if metadata_handler == MetadataHandler.correctly_structured.value:
        with open(source.get_metadata_file_path()) as f:
            metadata_dict = json.load(f)
            json_validate(metadata_dict, valid_metadata_schema)
    """
    elif metadata_handler == MetadataHandler.some_other_structure.value:
        # if another metadata structure is being used, only validate that it
        # is in a format that can be converted to what is needed, not actually
        # converted
        with open(source.get_metadata_file_path()) as f:
            metadata_dict = json.load(f)
            json_validate(metadata_dict, some_other_metadata_schema)
    """
    else:
        log_as_incomplete()
        return 
            "statusCode": 200, 
            "body": {"valid": False}
            }

    log_as_complete()
    return {
        "statusCode": 200, 
        "body": {"valid": True}
        }
    
