import logging
import json
import os
import time
import requests

from lambdautils.helpers import log_as_incomplete, log_as_complete, json_validate
from lambdautils.mocking import (
    get_dataset_api_client,
    get_lambda_client,
    get_recipe_api_client,
)
from lambdautils.schemas import (
    source_bucket_schema,
    valid_metadata_schema,
    upload_initialise_payload_schema,
    finaliser_payload_schema
)


def handler(event, context):
    """
    Triggered by opendata-source-extractor-lambda
    Invokes opendata-v4-upload-metadata-parser
    Posts new job, updates state of job
    Invokes opendata-v4-upload-poller
    """

    client = get_lambda_client()

    # Validate that the event matches the schema "transform_evocation_payload_schema"
    json_validate(event, upload_initialise_payload_schema)
    source_dict = event["source"]
    json_validate(source_dict, source_bucket_schema)
    s3_url = event["s3_url"]


    # TODO give lambda public internet access
    """
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

    """

    
    ###########################
    # to be removed
    payload_dict = {
        "statusCode": 200,
        "body": {
            "metadata": {
                "title": "I am the title of a thing"
                 },
            "dimension_data": {},
            "usage_notes": {}
            }
        }
    ###########################


    metadata_dict = payload_dict["body"]
    json_validate(metadata_dict, valid_metadata_schema)
    print('Validated: valid_metadata_schema')

    # starting api calls    
    recipe_api = get_recipe_api_client()
    dataset_api = get_dataset_api_client(s3_url=s3_url)

    # Use the apis to initialise the upload
    dataset_id = event["dataset_id"]
    recipe = recipe_api.get_recipe(dataset_id)
    print("Recipe got") 


    job_id, instance_id = dataset_api.post_new_job(recipe)
    dataset_api.update_state_of_job(job_id)
    print("Job state updated")

    ###########################
    return {
        "job_id": job_id, "instance_id": instance_id
        }
    ###########################

    time.sleep(60)

    # Start polling
    finaliser_payload = {
        "instance_id": instance_id,
        "metadata": metadata_dict,
        "dataset_details": event,
    }
    json_validate(finaliser_payload, finaliser_payload_schema) 

    # Start poller
    client.invoke(
       FunctionName="opendata-v4-upload-poller",
       InvocationType="Event",
       Payload=json.dumps(finaliser_payload),
    )
    log_as_complete()
