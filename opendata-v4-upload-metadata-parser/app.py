import logging
import json
import requests

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    json_validate,
    Source,
    MetadataHandler,
    COMMON_ZIP_PATH,
    empty_tmp_folder,
    cmd_csvw_metadata_parser,
)
from lambdautils.mocking import get_s3_client
from lambdautils.schemas import upload_metadata_parser_event_schema


def handler(event, context):
    """
    Triggered by opendata-v4-upload-initialiser
    Gets the name of metadata file and metadata structure from manifest.json 
    Transforms metadata if needed
    Returns metadata
    """

    json_validate(event, upload_metadata_parser_event_schema)

    # empty /tmp/ 
    empty_tmp_folder()

    s3 = get_s3_client()
    bucket = event["bucket"]
    zip_file = event["zip_file"]

    with open(COMMON_ZIP_PATH, "wb") as f:
        s3.download_fileobj(bucket, zip_file, f)
    
    print("Zip file downloaded from s3")

    source = Source(COMMON_ZIP_PATH)
    metadata_handler = source.get_metadata_handler()

    # The correctly_structured handler is for where the metadata json should already
    # be in the shape we want
    if metadata_handler == MetadataHandler.correctly_structured.value:

        print(f"Calling metadata handler for {MetadataHandler.correctly_structured.value}")
        with open(source.get_metadata_file_path()) as f:
            metadata_dict = json.load(f)
            
    # The cmd_csvw handler is for when the metadata json is in the format that 
    # is created by CMD
    elif metadata_handler == MetadataHandler.cmd_csvw.value:

        print(f"Calling metadata handler for {MetadataHandler.cmd_csvw.value}")
        with open(source.get_metadata_file_path()) as f:
            cmd_csvw_metadata_dict = json.load(f)
            # do the transform of the metadata here, want it in the 
            # valid_metadata_schema format
            metadata_dict = cmd_csvw_metadata_parser(cmd_csvw_metadata_dict)
            
    else:

        log_as_incomplete()
        raise ValueError(f"Unknown metadata handler {metadata_handler}")

    
    log_as_complete()
    return {
        "statusCode": 200, 
        "body": metadata_dict,
        "request_id": event["request_id"]
        }
