import requests
import sys
import json
import os
from databaker.framework import *
import pandas as pd

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    json_validate,
    COMMON_ZIP_PATH,
    Source,
    empty_tmp_folder,
    request_id_check
)

from lambdautils.mocking import get_s3_client, get_lambda_client, get_upload_api_client
from lambdautils.schemas import transformer_event_schema, transform_retriever_response_schema


def handler(event, context):
    """
    Currently testing
    """
    json_validate(event, transformer_event_schema)
    # empty /tmp/ 
    empty_tmp_folder() 

    # initialising clients
    s3 = get_s3_client() 
    client = get_lambda_client()
    upload_api = get_upload_api_client()

    bucket = event["source"]["bucket"]
    zip_file = event["source"]["zip_file"]
    transform_repo = event["transform"]

    with open(COMMON_ZIP_PATH, "wb") as f:
        s3.download_fileobj(bucket, zip_file, f)

    print("Zip file downloaded from s3")
    
    source = Source(COMMON_ZIP_PATH)
    datafiles = source.get_data_file_paths()

    retriever_event = {
        "transform": event["transform"],
        "request_id": event["request_id"]
    }
    
    r = client.invoke(
        FunctionName="opendata-transform-retriever",
        InvocationType="RequestResponse",
        Payload=json.dumps(retriever_event),
    )
    
    print("opendata-transform-retriever invoked")
    payload_dict = json.load(r["Payload"])
    json_validate(payload_dict, transform_retriever_response_schema)
    request_id_check(event, payload_dict) 
    
    script = payload_dict["body"]
    transform_script = "/tmp/transform_script.py"
    # writing transform file to /tmp/
    with open(transform_script, "w") as f:
        f.write(script)
        f.close()
    print(f"transform script wrote as {transform_script}")

    requirements_dict = payload_dict["requirements"]
    if requirements_dict: # if requirements not empty
        for module in requirements_dict:
            file_name = f"/tmp/{module}.py".replace("-", "_")
            module_script = requirements_dict[module]
            with open(file_name, "w") as f:
                f.write(module_script)
                f.close()
            print(f"module script wrote as {file_name}")

    sys.path.append("/tmp/")
    from transform_script import transform
    # catch any errors in the transform
    try:
        v4_path = transform(datafiles)
    except Exception as e:
        print("Error in transform")
        raise Exception(e)

    # TODO - when more than one v4 is produced
    # 'metadata_<dataset_id>' in manifest.json
    
    # upload the file
    s3_url = upload_api.post_v4_to_s3(v4_path)

    event["s3_url"] = s3_url
    del event["transform"] # no longer needed

    r = client.invoke(
        FunctionName="opendata-v4-upload-initialiser",
        InvocationType="Event",
        Payload=json.dumps(event),
    )

    print("opendata-v4-upload-initialiser")
    log_as_complete() 

    return {
        "statusCode": 200, 
        "body": "lambda completed",
        "request_id": event["request_id"]
    }

