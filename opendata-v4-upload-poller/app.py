import logging
import json
import os
import time
import datetime

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    json_validate,
)
from lambdautils.schemas import finaliser_payload_schema
from lambdautils.mocking import get_dataset_api_client, get_lambda_client


def handler(event, context):
    """
    Principle lambda event handler.
    """

    access_token = os.environ.get("ZEBEDEE_ACCESS_TOKEN", None)
    if not access_token:
        raise ValueError("Aborting. Need a zebedee access token.")

    client = get_lambda_client()
    dataset_api = get_dataset_api_client(access_token)

    json_validate(event, finaliser_payload_schema)

    # Env vars we're gonna need
    maximum_polling_time = os.environ.get("MAXIMUM_POLLING_TIME", None)
    if not maximum_polling_time:
        log_as_incomplete()
        raise Exception("Lambda cannot run without env var MAXIMUM_POLLING_TIME")

    delay_between_checks = os.environ.get("DELAY_BETWEEN_CHECKS", None)
    if not delay_between_checks:
        log_as_incomplete()
        raise Exception("Lambda cannot run without env var DELAY_BETWEEN_CHECKS")

    start_time = datetime.datetime.now().isoformat()

    while True:
        complete = dataset_api.upload_complete(event["instance_id"])
        logging.warning(f'complete: {complete}')

        if complete:

                # Call next lambda, finish, dont start another one of these
                client.invoke(
                    FunctionName="opendata-v4-upload-finaliser",
                    InvocationType="Event",
                    Payload=json.dumps(event),
                )
                log_as_complete()
                break
        elif datetime.datetime.now() > (datetime.datetime.fromisoformat(start_time) + datetime.timedelta(0, int(maximum_polling_time))):
            client.invoke(
                        FunctionName="opendata-v4-upload-poller",
                        InvocationType="Event",
                        Payload=json.dumps(event),
                    )
            logging.warning('New poller invoked')
            break
        else:
            time.sleep(int(delay_between_checks))
