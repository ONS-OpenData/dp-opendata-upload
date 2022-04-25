import datetime
import json

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    json_validate,
    COMMON_ZIP_PATH,
    Source,
    empty_tmp_folder,
)
from lambdautils.mocking import get_s3_client, get_lambda_client, get_upload_api_client
from lambdautils.schemas import source_extractor_event_schema


def handler(event, context):
    """
    Used when original data is in v4 format - no transform required
    Triggered by opendata-transform-decision-lambda
    Gets v4 from source, uploads to publishing bucket using upload api
    Invokes opendata-v4-upload-initialiser lambda
    """
    # empty /tmp/ 
    empty_tmp_folder()

    json_validate(event, source_extractor_event_schema) 
    
    client = get_lambda_client()
    s3 = get_s3_client() 
    upload_api = get_upload_api_client()
    
    bucket = event["source"]["bucket"]
    zip_file = event["source"]["zip_file"]
    
    with open(COMMON_ZIP_PATH, "wb") as f:
        s3.download_fileobj(bucket, zip_file, f)
    
    source = Source(COMMON_ZIP_PATH)
    datafiles = source.get_data_file_paths()

    if len(datafiles) != 1 or not str(datafiles[0]).endswith(".csv"):
        log_as_incomplete()
        raise ValueError(
            f"Zip file must contain exactly one data file of csv format. Got {datafiles}"
        )
    v4_path = datafiles[0]

    # upload the file
    s3_url = upload_api.post_v4_to_s3(v4_path)
    
    event["s3_url"] = s3_url
    del event["transform"] # no longer needed

    r = client.invoke(
        FunctionName="opendata-v4-upload-initialiser",
        InvocationType="Event",
        Payload=json.dumps(event),
    )

    log_as_complete()

    return {
        "statusCode": 200, 
        "body": "lambda completed"
    }

    
        
