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
from lambdautils.schemas import upload_poller_event_schema
from lambdautils.mocking import get_dataset_api_client, get_lambda_client


def handler(event, context):
    """
    Triggered by opendata-v4-upload-initialiser
    Gets polling details
    Checks state of instance upload
    When finished invokes opendata-v4-upload-finaliser
    Invokes itself and closes current when time limit exceeded
    """
    
    #message = json.loads(event["Records"][0]["Sns"]["Message"])

    json_validate(event, upload_poller_event_schema)

    client = get_lambda_client()
    dataset_api = get_dataset_api_client()


    time.sleep(60) # waits for instance to begin

    # Env vars we're gonna need
    maximum_polling_time = os.environ.get("MAXIMUM_POLLING_TIME", None)
    if not maximum_polling_time:
        log_as_incomplete()
        msg = "Lambda cannot run without env var MAXIMUM_POLLING_TIME"
        logging.error(msg)
        raise Exception(msg)

    delay_between_checks = os.environ.get("DELAY_BETWEEN_CHECKS", None)
    if not delay_between_checks:
        log_as_incomplete()
        msg = "Lambda cannot run without env var DELAY_BETWEEN_CHECKS"
        logging.error(msg)
        raise Exception(msg)

    start_time = datetime.datetime.now()
    current_count = event["count"]

    if current_count == 5:
        log_as_incomplete()
        print("Poller has been invoked max number of times")
        return {"body": "Poller has been invoked max number of times"}

    while True:
        
        if dataset_api.upload_complete(event["instance_id"]):
            del event["count"]

            # Call next lambda, finish, dont start another one of these
            client.invoke(
                FunctionName="opendata-v4-upload-finaliser",
                InvocationType="Event",
                Payload=json.dumps(event),
            )
            log_as_complete()
            return {"body": "lambda complete"}
        

        elif datetime.datetime.now() > (start_time + datetime.timedelta(0, int(maximum_polling_time))):

            current_count += 1
            event["count"] = current_count

            client.invoke(
                        FunctionName="opendata-v4-upload-poller",
                        InvocationType="Event",
                        Payload=json.dumps(event),
                    )
            print("New poller invoked")
            logging.warning("New poller invoked")
            return {"body": "lambda invoking itself"}

        else:
            print("Waiting before going back through the loop")
            time.sleep(int(delay_between_checks))
