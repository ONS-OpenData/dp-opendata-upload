import json
import os
import logging
import zipfile

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
        Source,
        MetadataHandler,
        COMMON_ZIP_PATH,
    )
    from ..common.mocking import get_s3_client
    from ..common.schemas import source_bucket_schema, valid_metadata_schema
except ImportError:
    from helpers import (
        log_as_incomplete,
        log_as_complete,
        json_validate,
        Source,
        MetadataHandler,
        COMMON_ZIP_PATH,
    )
    from mocking import get_s3_client
    from schemas import source_bucket_schema, valid_metadata_schema


def handler(event, context):
    """
    Principle lambda event handler.
    """

    s3 = get_s3_client()

    # Validate that the event matches the schema "source_bucket_schema"
    json_validate(event, source_bucket_schema)
    bucket = event["bucket"]
    zip_file = event["zip_file"]

    with open(COMMON_ZIP_PATH, "wb") as f:
        s3.download_fileobj(bucket, zip_file, f)

    source = Source(COMMON_ZIP_PATH)
    metadata_handler = source.get_metadata_handler()

    # The simple_json handler is for where the metadata json should already
    # in the shape we want
    if metadata_handler == MetadataHandler.correctly_structured.value:
        with open(source.get_metadata_file_path()) as f:
            metadata_dict = json.load(f)
            json_validate(metadata_dict, valid_metadata_schema)

    log_as_complete()
    return {"statusCode": 200, "body": json.dumps(metadata_dict)}
