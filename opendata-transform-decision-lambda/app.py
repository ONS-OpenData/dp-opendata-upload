import logging
import json

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    TransformType,
    json_validate,
)
from lambdautils.mocking import get_lambda_client
from lambdautils.schemas import (
    transform_decision_event_schema,
    transform_details_response_schema,
)


def handler(event, context):
    """
    Triggered by upload into s3 bucket
    Invokes opendata-transform-details-lambda
    Invokes one of the transform lambdas
    """
    # Delete next 2 rows, currently there to stop lambda triggering when a new zip file is uploaded
    print("Lambda turned off")
    return {"body": "Lambda turned off"}
    
    json_validate(event, transform_decision_event_schema) 

    # Creating a unique identifier, to always be passed along
    # TODO - generate this
    request_id = "opendata_1234-abcd-5678-efgh" 

    client = get_lambda_client()
    
    record = event.get("Records")[0]
    bucket = record["s3"]["bucket"]["name"]
    zip_file = record["s3"]["object"]["key"]

    source_dict = {
        "bucket": bucket, 
        "zip_file": zip_file,
        "request_id": request_id
        }

    r = client.invoke(
        FunctionName="opendata-transform-details-lambda",
        InvocationType="RequestResponse",
        Payload=json.dumps(source_dict),
    )

    payload_dict = json.load(r["Payload"])
    json_validate(payload_dict, transform_details_response_schema)
    if payload_dict["statusCode"] != 200:
        log_as_incomplete()
        raise Exception(
            f"Failed to get response from opendata-transform-details-lambda, with status code {payload_dict['statusCode']}"
        ) 

    transform_details = payload_dict["body"]["transform_details"]
    transform_type = transform_details["transform_type"]
    del source_dict["request_id"] # goes on top level of dict
    transform_details["source"] = source_dict
    transform_details["request_id"] = request_id
    del transform_details["transform_type"]  # no longer needed

    logging.info(f"Transform type is {transform_type}")
    print(f"Transform type is {transform_type}")

    
    if transform_type == TransformType.long.value:
        log_as_incomplete()
        raise NotImplementedError("Not looking at long running transforms yet.")

    elif transform_type == TransformType.none.value:
        print("Invoking opendata-source-extractor-lambda")

        r = client.invoke(
            FunctionName="opendata-source-extractor-lambda",
            InvocationType="Event",
            Payload=json.dumps(transform_details),
        )
        
        log_as_complete()
        return {
            "statusCode": 200,
            "body": "lambda completed, invoked opendata-source-extractor-lambda",
            "request_id": request_id
        }

    elif transform_type == TransformType.short.value:
        print("Invoking opendata-transformer-lambda")

        r = client.invoke(
            FunctionName="opendata-transformer-lambda",
            InvocationType="Event",
            Payload=json.dumps(transform_details),
        )
        
        log_as_complete()
        return {
            "statusCode": 200,
            "body": "lambda completed, invoked opendata-transformer-lambda",
            "request_id": request_id
        }

    else:
        log_as_incomplete()
        raise ValueError(
            f"Unknown transform type {transform_type}. Should be one of {TransformType.values()}"
        ) 
