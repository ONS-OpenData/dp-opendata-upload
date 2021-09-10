import logging
import json

from lambdautils.helpers import log_as_incomplete, log_as_complete, json_validate
from lambdautils.mocking import get_s3_client, get_lambda_client
from lambdautils.schemas import (
    source_bucket_schema,
    bucket_notification_v4_event_schema,
    valid_metadata_schema,
)


def handler(event, context):
    """
    Principle lambda event handler.
    """

    client = get_lambda_client()
    s3 = get_s3_client()

    json_validate(event, bucket_notification_v4_event_schema)
    records = event.get("Records", None)
    record = records[0]

    bucket = record["s3"]["bucket"]["name"]
    v4_file = record["s3"]["object"]["key"]

    # get source bucket information from s3 object attribute,
    # drop out early if its not an automated upload.
    object_response = s3.head_object(Bucket=bucket, Key=v4_file)
    try:
        source_dict = object_response["Metadata"]["source"]
        json_validate(source_dict, source_bucket_schema)
    except KeyError:
        logging.info("Not an automated upload, ending process.")
        return

    # Fetch the metadata for it
    r = client.invoke(
        FunctionName="opendata-v4-upload-metadata-parser",
        InvocationType="RequestResponse",
        Payload=json.dumps(source_dict),
    )
    payload_dict = json.load(r["Payload"])
    if payload_dict["statusCode"] != 200:
        log_as_incomplete()
        raise Exception(
            f"Failed to get response from opendata-transform-details-lambda, with status code {payload_dict['statusCode']}"
        )

    metadata_dict = json.loads(payload_dict["body"])
    json_validate(metadata_dict, valid_metadata_schema)

    # At this point we have
    # metadata_dict = the metadata for the upload
    # source_dict = dict with bucket + v4 filename, this is the means to get the v4 file.
    # this should be all we need to trigger the uploads

    # TODO - the actual upload

    log_as_complete()
