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
    object_response = s3.head_object(Bucket=bucket, Key=v4_file)

    try:
        #source_dict = json.loads(object_response)["Metadata"]["source"]
        #json_validate(source_dict, source_bucket_schema)
        transform_details = json.loads(object_response["Metadata"]["transform_details"])
        json_validate(transform_details, transform_evocation_payload_schema)
        source_dict = transform_details["source"]
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

    del transform_details["source"]
    json_validate(transform_details, transform_details_schema)

    # Use the apis to initialise the upload
    recipe = recipe_api.get_recipe(transform_details["dataset_id"])

    job_id, instance_id = dataset_api.post_new_job(v4_file, recipe)
    dataset_api.update_state_of_job(job_id)

    logging.warning(job_id)
    logging.warning(instance_id) 
    
    raise NotImplementedError  # We got this far before hitting the networking hurdle,
    # When its done and if we're getting to this error AND we're getting back the expected job_id and instance_id then
    # you can remove the above logging and error and continue uncommenting/trying the below code.

    # gives cmd apps a chance to 'kick off' import process, observations do not import
    # straight away and would cause the poller to KeyError
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
