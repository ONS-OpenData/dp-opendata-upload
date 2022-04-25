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
    COMMON_ZIP_PATH,
    empty_tmp_folder,
)

from lambdautils.mocking import get_s3_client
from lambdautils.schemas import metadata_validator_event_schema, valid_metadata_schema, cmd_metadata_schema


def handler(event, context):
    """
    Triggered by opendata-transform-details-lambda
    Gets the name of metadata file and metadata structure from manifest.json 
    Determins if metadata in source is in a valid format
    Returns {valid:True/False} 
    """

    json_validate(event, metadata_validator_event_schema)

    # empty /tmp/ 
    empty_tmp_folder()

    # initialising clients
    s3 = get_s3_client()

    bucket = event["bucket"]
    zip_file = event["zip_file"]

    with open(COMMON_ZIP_PATH, "wb") as f:
        s3.download_fileobj(bucket, zip_file, f)

    print("Zip file downloaded from s3")

    source = Source(COMMON_ZIP_PATH)
    metadata_handler = source.get_metadata_handler()

    # The correctly_structured handler is for when the metadata json should already
    # be in the shape we want
    if metadata_handler == MetadataHandler.correctly_structured.value:
        
        with open(source.get_metadata_file_path()) as f:
            metadata_dict = json.load(f)
            json_validate(metadata_dict, valid_metadata_schema)
        
    # The cmd_csvw handler is for when the metadata json is in the format that 
    # is created by CMD
    elif metadata_handler == MetadataHandler.cmd_csvw.value:
        
        with open(source.get_metadata_file_path()) as f:
            metadata_dict = json.load(f)
            json_validate(metadata_dict, cmd_metadata_schema)
        
    else:
        log_as_incomplete()
        return {
            "statusCode": 200, 
            "body": {"valid": False},
            "request_id": event["request_id"]
            }

    log_as_complete()
    return {
        "statusCode": 200, 
        "body": {"valid": True},
        "request_id": event["request_id"]
        }
    
