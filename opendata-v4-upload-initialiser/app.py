import logging
import json

from lambdautils.helpers import log_as_incomplete, log_as_complete, json_validate
from lambdautils.mocking import (
    get_dataset_api_client,
    get_s3_client,
    get_lambda_client,
    get_zebedee_client,
    get_recipe_api_client,
)
from lambdautils.schemas import (
    source_bucket_schema,
    bucket_notification_v4_event_schema,
    valid_metadata_schema,
    transform_details_schema,
    finaliser_payload_schema,
)


def handler(event, context):
    """
    Principle lambda event handler.
    """

    client = get_lambda_client()
    s3 = get_s3_client()
    zebedee = get_zebedee_client()
    recipe_api = get_recipe_api_client()
    dataset_api = get_dataset_api_client()

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
        logging.warning("Not an automated upload, ending process.")
        return

    # Fetch the metadata the v4 will need from the metadata parser
    r = client.invoke(
        FunctionName="opendata-v4-upload-metadata-parser",
        InvocationType="RequestResponse",
        Payload=json.dumps(source_dict),
    )

    payload_dict = json.load(r["Payload"])
    if payload_dict["statusCode"] != 200:
        log_as_incomplete()
        raise Exception(
            f"Failed to get response from opendata-v4-upload-metadata-parser, with status code {payload_dict['statusCode']}"
        )
    metadata_dict = json.loads(payload_dict["body"])
    json_validate(metadata_dict, valid_metadata_schema)

    # Get transform details from the transform details lambda
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

    # Use the apis to initialise the upload
    access_token = zebedee.get_access_token()
    recipe = recipe_api.get_recipe(access_token, transform_details["dataset_id"])
    job_id, instance_id = dataset_api.post_new_job(access_token, v4_file, recipe)
    dataset_api.update_state_of_job(access_token, job_id)

    # Start polling
    finaliser_payload = {
        "instance_id": instance_id,
        "metadata": metadata_dict,
        "transform_details": transform_details,
    }
    json_validate(finaliser_payload, finaliser_payload_schema)

    # Start poller
    client.invoke(
        FunctionName="opendata-v4-upload-poller",
        InvocationType="Event",
        Payload=json.dumps(finaliser_payload),
    )
    log_as_complete()
