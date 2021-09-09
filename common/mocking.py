from io import BytesIO, FileIO
import os
import json
import shutil

import boto3

from helpers import COMMON_ZIP_PATH


def payload(payload_dict: dict):
    """
    Wrap creating payload as there's a lot of boiler plate to
    get in in a form/type that matches that returned by
    the boto3 lambda client.
    """
    if "body" in payload_dict:
        payload_dict["body"] = json.dumps(payload_dict["body"])
    return {
        "Payload": BytesIO(
            initial_bytes=bytes(json.dumps(payload_dict), encoding="utf-8")
        )
    }


def get_s3_client():
    """When testing return a mock client for interacting with boto3 s3"""
    if os.environ.get("IS_TEST", None):
        return MockS3Client()
    return boto3.client("s3")


def get_lambda_client():
    """When testing return a mock client for interacting with boto3 lambda"""
    if os.environ.get("IS_TEST", None):
        return MockLambdaClient()
    return boto3.client("lambda")


class MockLambdaClient:
    def __init__(self):
        # Get the name of the start json fixture from an env var. i.e what our test passes in as "event"
        # Example: features/fixtures/opendata-transform-decision-lambda/events/no_bucket_name.json
        initial_event_fixture = os.environ.get("EVENT_FIXTURE", None).strip()
        if not initial_event_fixture:
            raise ValueError(
                'Aborting. Test container needs to have an envionment variable of "EVENT_FIXTURE".'
            )

        # From here, we just use the name of the fixture to decide what mock responses are
        # getting returned.

        # Any test thats meant to fail before you client.invoke() go here - they dont need a mocked response
        if initial_event_fixture in [
            "opendata-transform-decision-lambda/events/no_bucket_name.json",
            "opendata-transform-decision-lambda/events/no_object_key.json",
        ]:
            self.mock_responses = []

        # For everything else, just return based on the fixture we've passed in
        # If your lambda test invokes once - provide a list of 1
        # If it invokes twice - provide a list of 2
        # etc
        elif (
            initial_event_fixture
            == "opendata-transform-decision-lambda/events/failed_response_details_lambda.json"
        ):
            self.mock_responses = [payload({"statusCode": 500})]
        elif (
            initial_event_fixture
            == "opendata-transform-decision-lambda/events/valid.json"
        ):
            self.mock_responses = [
                payload(
                    {
                        "body": {
                            "transform_details": {
                                "transform": "",
                                "collection_id": "",
                                "transform_type": "none",
                                "dataset_id": "",
                                "edition_id": "",
                                "collection_name": "",
                            }
                        },
                        "statusCode": 200,
                    }
                ),
                payload({"statusCode": 200}),
            ]
        elif (
            initial_event_fixture
            == "opendata-transform-details-lambda/events/valid.json"
        ):
            self.mock_responses = [
                payload({"body": {"valid": "True"}, "statusCode": 200})
            ]

        elif (
            initial_event_fixture
            == "opendata-transform-details-lambda/events/failed_response_metadata_validator.json"
        ):
            self.mock_responses = [payload({"statusCode": 500})]

        else:
            raise ValueError(
                f'You are calling MockLambdaClient but no responsers for the starting event "{initial_event_fixture}" have been defined.'
            )

    def invoke(self, FunctionName: str, InvocationType: str, Payload: str):
        try:
            mock_response = self.mock_responses.pop(0)
            return mock_response
        except IndexError as err:
            raise IndexError(
                "Could not find a mock, have you defined one self.mock_responses for _every_ invoke in this test?"
            ) from err


class MockS3Client:
    def __init__(self):
        initial_event_fixture = os.environ.get("EVENT_FIXTURE", None)
        if not initial_event_fixture:
            raise ValueError(
                'Aborting. Test container needs to have an envionment variable of "EVENT_FIXTURE".'
            )
        self.initial_event_fixture = initial_event_fixture

    def download_fileobj(self, bucket: str, zip_file: str, f: FileIO):

        if (
            self.initial_event_fixture
            == "opendata-v4-upload-metadata-parser/events/valid.json"
        ):
            shutil.copy("/tmp/zips/valid1.zip", COMMON_ZIP_PATH)

    def head_object(self, Bucket=None, Key=None):
        assert Bucket, "Mock s3 method required both the Bucket and Key kwargs"
        assert Key, "Mock s3 method required both the Bucket and Key kwargs"
        yield next(self.mock_responses)
