import logging
import json
import os
import time
import requests
#import boto3

from lambdautils.helpers import log_as_incomplete, log_as_complete, json_validate
from lambdautils.mocking import (
    get_dataset_api_client,
    get_lambda_client,
    get_recipe_api_client,
)
from lambdautils.schemas import (
    upload_initialiser_event_schema,
    upload_metadata_parser_response_schema
)


def handler(event, context):
    """
    Triggered by opendata-source-extractor-lambda
    Invokes opendata-v4-upload-metadata-parser
    Posts new job, updates state of job
    Invokes opendata-v4-upload-poller
    """
    
    """
    sns = boto3.client('sns')

    sns.publish(
        TopicArn="arn:aws:sns:eu-west-1:352437599875:sns-opendata-test",
        Message=json.dumps(event)
    )
    
    return {"body": "completed"}
    """
    


    json_validate(event, upload_initialiser_event_schema)

    client = get_lambda_client()
    source_dict = event["source"]
    source_dict["request_id"] = event["request_id"]
    s3_url = event["s3_url"]


    # TODO give lambda public internet access
    # Fetch the metadata the v4 will need from the metadata parser
    r = client.invoke(
        FunctionName="opendata-v4-upload-metadata-parser",
        InvocationType="RequestResponse",
        Payload=json.dumps(source_dict),
    )

    payload_dict = json.load(r["Payload"])
    json_validate(payload_dict, upload_metadata_parser_response_schema)
    if payload_dict["statusCode"] != 200:
        log_as_incomplete()
        raise Exception(
            f"Failed to get response from opendata-v4-upload-metadata-parser, with status code {payload_dict['statusCode']}"
        )


    metadata_dict = payload_dict["body"]

    # starting api calls    
    recipe_api = get_recipe_api_client()
    dataset_api = get_dataset_api_client()

    # Use the apis to initialise the upload
    dataset_id = event["dataset_id"]
    recipe = recipe_api.get_recipe(dataset_id)

    job_id, instance_id = dataset_api.post_new_job(recipe, s3_url)
    dataset_api.update_state_of_job(job_id)
    print("Job state updated")

    # Start polling
    poller_dict = {
        "instance_id": instance_id,
        "metadata_dict": metadata_dict,
        "dataset_details": event,
        "count": 0,
        "request_id": event["request_id"]
    } 

    # remove unwanted from poller_dict
    del poller_dict["dataset_details"]["source"]
    del poller_dict["dataset_details"]["s3_url"]
    del poller_dict["dataset_details"]["request_id"] # moved to top level of dict

    # Start poller
    client.invoke(
       FunctionName="opendata-v4-upload-poller",
       InvocationType="Event",
       Payload=json.dumps(poller_dict),
    )
    
    log_as_complete()
    return {"body": "lambda complete"}
