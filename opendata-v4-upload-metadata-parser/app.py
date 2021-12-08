import logging
import json

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    json_validate,
    Source,
    MetadataHandler,
    COMMON_ZIP_PATH,
)
from lambdautils.mocking import get_s3_client
from lambdautils.schemas import source_bucket_schema, valid_metadata_schema


def handler(event, context):
    """
    Triggered by opendata-v4-upload-initialiser
    Gets the name of metadata file and metadata structure from manifest.json 
    Transforms metadata if needed
    Returns metadata
    """

    s3 = get_s3_client()

    # Validate that the event matches the schema "source_bucket_schema"
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
        with open(source.get_metadata_file_path()) as f:
            other_structure_metadata_dict = json.load(f)
            # do the transform of the metadata here, want it in the 
            # valid_metadata_schema format
            metadata_dict = function(other_structure_metadata_dict)
            json_validate(metadata_dict, valid_metadata_schema)
        """
    else:
        log_as_incomplete()
        raise ValueError(f"Unknown metadata handler {metadata_handler}")

    log_as_complete()
    metadata_body = json.dumps(metadata_dict)
    print(f'Returning status code 200 and {metadata_body}')
    return {"statusCode": 200, "body": metadata_body}
