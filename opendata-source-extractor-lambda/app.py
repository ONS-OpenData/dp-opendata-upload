import datetime
import json

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    json_validate,
    COMMON_ZIP_PATH,
    V4_BUCKET_NAME,
    Source,
)
from lambdautils.mocking import get_s3_client
from lambdautils.schemas import transform_evocation_payload_schema


def handler(event, context):
    """
    Principle lambda event handler.
    """

    s3 = get_s3_client()

    # Validate that the event matches the schema "transform_evocation_payload_schema"
    json_validate(event, transform_evocation_payload_schema)
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

    # Uploads the v4 to the v4 upload bucket with an attribute linking
    # it back to its original source (and metadata)
    extra_args = {
        "Metadata": {"source": json.dumps({"bucket": bucket, "zip_file": zip_file})}
    }  # 'x-amz-meta-' is added by the api

    # for S3 object_name use file_name without /tmp/
    # removing the '.' from file name - need to confirm this
    # timestamp for uniqueness
    timestamp = datetime.datetime.now()  # to be ued as unique resumableIdentifier
    timestamp = datetime.datetime.strftime(timestamp, "%d%m%y%H%M%S")
    object_name = f"{timestamp}-{v4_path.split('/')[-1].replace('.', '')}"

    # Upload the file
    try:
        with open(v4_path, "rb") as f:
            s3.upload_fileobj(f, V4_BUCKET_NAME, object_name, ExtraArgs=extra_args)
        log_as_complete()
    except Exception as err:
        log_as_incomplete()
        raise err
