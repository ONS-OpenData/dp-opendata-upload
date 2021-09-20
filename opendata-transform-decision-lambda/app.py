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
    bucket_notification_source_event_schema,
    transform_details_schema,
    source_bucket_schema,
    transform_evocation_payload_schema,
)


def handler(event, context):
    """
    Principle lambda event handler.
    """

    client = get_lambda_client()

    json_validate(event, bucket_notification_source_event_schema)
    record = event.get("Records")[0]
    bucket = record["s3"]["bucket"]["name"]
    zip_file = record["s3"]["object"]["key"]

    source_dict = {"bucket": bucket, "zip_file": zip_file}
    json_validate(source_dict, source_bucket_schema)

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
    transform_type = transform_details.get("transform_type")

    if transform_type == TransformType.long.value:
        log_as_incomplete()
        raise NotImplementedError("Not looking at long running transforms yet.")

    elif transform_type == TransformType.none.value:
        logging.info(f'Transform type is {transform_type}')

        transform_details["source"] = source_dict
        del transform_details["transform_type"]  # no longer needed
        json_validate(transform_details, transform_evocation_payload_schema)

        r = client.invoke(
            FunctionName="opendata-source-extractor-lambda",
            InvocationType="Event",
            Payload=json.dumps(transform_details),
        )
        log_as_complete()

    elif transform_type == TransformType.short.value:
        log_as_incomplete()
        raise NotImplementedError("Not looking at short running transforms yet.")

    else:
        log_as_incomplete()
        raise ValueError(
            f"Unknown transform type {transform_type}. Should be one of {TransformType.values()}"
        )
