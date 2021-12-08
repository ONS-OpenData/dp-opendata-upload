import logging
import json
import os
import time

from lambdautils.helpers import log_as_incomplete, log_as_complete, json_validate
from lambdautils.mocking import (
    get_dataset_api_client,
    get_s3_client,
    get_lambda_client,
    get_recipe_api_client,
)
from lambdautils.schemas import (
    source_bucket_schema,
    bucket_notification_v4_event_schema,
    valid_metadata_schema,
    transform_details_schema,
    transform_evocation_payload_schema,
    finaliser_payload_schema
)


def handler(event, context):
    """
    Triggered by data being upload to secon s3 bucket (by one of transform lambdas)
    Gets transform details from s3 object (the v4)
    Invokes opendata-v4-upload-metadata-parser
    Posts new job, updates state of job
    Invokes opendata-v4-upload-poller
    """

    access_token = os.environ.get("ZEBEDEE_ACCESS_TOKEN", None)
    if not access_token:
        raise ValueError("Aborting. Need a zebedee access token.")

    s3_url = os.environ.get("S3_V4_BUCKET_URL", None)
    if not s3_url:
        raise ValueError("Aborting. Need a s3 bucket url.")

    client = get_lambda_client()
    s3 = get_s3_client()
    recipe_api = get_recipe_api_client(access_token)
    dataset_api = get_dataset_api_client(access_token, s3_url=s3_url)

    json_validate(event, bucket_notification_v4_event_schema)
    records = event.get("Records", None)
    record = records[0]

    bucket = record["s3"]["bucket"]["name"]
    v4_file = record["s3"]["object"]["key"]

    # get source bucket information from s3 object attribute,
    # drop out early if its not an automated upload.
    object_response_dict = s3.head_object(Bucket=bucket, Key=v4_file)

    # TODO - this should be first, not point instantiating clients (above) we don't need to use
    try:
        transform_details = object_response_dict["Metadata"]["transform_details"]
        json_validate(transform_details, transform_evocation_payload_schema)
        source_dict = transform_details["source"]
        json_validate(source_dict, source_bucket_schema)

        print('Validated: source_bucket_schema')
    except KeyError:
        if "Metadata" not in object_response_dict:
            msg = 'No "Metadata" key on object.'
        elif "source" not in object_response_dict["Metadata"]:
            msg = f'No "source" subkey in "Metadata" field of object. Got {object_response_dict.keys()}'
        logging.warning('Not an automated upload, ending.\n' + msg)
        return
    print('Confirmed as automated upload.')

    # Fetch the metadata the v4 will need from the metadata parser
    r = client.invoke(
        FunctionName="opendata-v4-upload-metadata-parser",
        InvocationType="RequestResponse",
        Payload=json.dumps(source_dict),
    )

    print("Response received")
    payload_dict = json.load(r["Payload"])
    if payload_dict["statusCode"] != 200:
        log_as_incomplete()
        raise Exception(
            f"Failed to get response from opendata-v4-upload-metadata-parser, with status code {payload_dict['statusCode']}"
        )
    metadata_dict = json.loads(payload_dict["body"])
    json_validate(metadata_dict, valid_metadata_schema)
    print('Validated: valid_metadata_schema')

    del transform_details["source"]
    json_validate(transform_details, transform_details_schema)
    print('Validated: transform_details_schema')

    # Use the apis to initialise the upload
    recipe = recipe_api.get_recipe(transform_details["dataset_id"])
    print("Recipe got")

    job_id, instance_id = dataset_api.post_new_job(v4_file, recipe)
    dataset_api.update_state_of_job(job_id)
    print("Job state updated")

    time.sleep(60)

    # Start polling
    finaliser_payload = {
        "instance_id": instance_id,
        "metadata": metadata_dict,
        "dataset_details": transform_details,
    }
    json_validate(finaliser_payload, finaliser_payload_schema) 

    # Start poller
    client.invoke(
       FunctionName="opendata-v4-upload-poller",
       InvocationType="Event",
       Payload=json.dumps(finaliser_payload),
    )
    log_as_complete()
