from io import BytesIO, FileIO
import os
import json
import shutil

import boto3

from .helpers import COMMON_ZIP_PATH
from .clients import ZebedeeClient, RecipeApiClient, DatasetApiClient


def get_s3_client():
    """When testing return a mock client for faking interactions with boto3 s3"""
    if os.environ.get("IS_TEST", None):
        return MockS3Client()
    return boto3.client("s3")


def get_lambda_client():
    """When testing return a mock client for faking interactions with boto3 lambda"""
    if os.environ.get("IS_TEST", None):
        return MockLambdaClient()
    return boto3.client("lambda")


def get_zebedee_client():
    """When testing return a mock client for faking interactions with zebedee"""
    if os.environ.get("IS_TEST", None):
        return MockZebedeeClient()
    return ZebedeeClient()


def get_recipe_api_client(access_token: str):
    """When testing return a mock client for faking interactions with the recipe api"""
    if os.environ.get("IS_TEST", None):
        return MockRecipeApiClient()
    return RecipeApiClient(access_token)


def get_dataset_api_client(access_token: str, s3_url: str = None):
    """When testing return a mock client for faking interactions with the dataset api"""
    if os.environ.get("IS_TEST", None):
        return MockDatasetApiClient()
    return DatasetApiClient(access_token, s3_url=s3_url)


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


class MockZebedeeClient:
    def __init__(self):

        msg = "ZebedeeClient required the exported environment variable: {}"

        for key in ["ZEBEDEE_URL"]:
            if not os.environ.get(key, None):
                raise AssertionError(msg.format(key))


class MockDatasetApiClient:
    def __init__(self):
        initial_event_fixture = os.environ.get("EVENT_FIXTURE", None).strip()
        if not initial_event_fixture:
            raise ValueError(
                'Aborting. Test container needs to have an envionment variable of "EVENT_FIXTURE".'
            )
        self.initial_event_fixture = initial_event_fixture

        assert os.environ.get("DATASET_API_URL", False)

        # from this point - mocks for self.upload_complete()
        # no mock needed
        if self.initial_event_fixture in [
            "opendata-v4-upload-initialiser/events/not_automated.json",
            "opendata-v4-upload-initialiser/events/no_bucket_name.json",
            "opendata-v4-upload-initialiser/events/valid.json",
            "opendata-v4-upload-poller/events/bad-starting-event.json"
        ]:
            return None # no mock needed
        elif (
            self.initial_event_fixture
            == "opendata-v4-upload-poller/events/valid.json"
        ):
            self.upload_complete_mocks = [True]

        elif (
            self.initial_event_fixture
            == "opendata-v4-upload-poller/events/valid-longer-polling.json"
        ):
            # So this call represents calling the lambda multiple times
            # Which means reinitialising this client multiple times.
            # We're going to use an env var to differentiate which invocation it is.
            mocked_calls_made = int(os.environ.get("MOCK_DATASET_API_CALLS", "0"))
            self.upload_complete_mocks = [
                [False, False, False, False],
                [False, False, False, False],
                [True]
            ][mocked_calls_made]
            mocked_calls_made += 1
            os.environ["MOCK_DATASET_API_CALLS"] = str(mocked_calls_made)
        else:
            raise ValueError(
                f'You are calling MockRecipeApiClient.upload_complete() but no responses for the starting event "{self.initial_event_fixture}" have been defined.'
            )

    def post_new_job(self, v4_file: str, recipe: dict):
        if (
            self.initial_event_fixture
            == "opendata-v4-upload-initialiser/events/valid.json"
        ):
            return "fake_job_id", "fake_instance_id"

        else:
            raise ValueError(
                f'You are calling MockRecipeApiClient.get_recipe() but no responses for the starting event "{self.initial_event_fixture}" have been defined.'
            )

    def update_state_of_job(self, job_id: str):
        assert os.environ.get("S3_V4_BUCKET_URL", False)
        if self.initial_event_fixture == "opendata-v4-upload-initialiser/events/valid.json":
            pass # its either pass or error

        else:
            raise ValueError(
                f'You are calling MockRecipeApiClient.update_state_of_job() but no responses for the starting event "{self.initial_event_fixture}" have been defined.'
            )

    def upload_complete(self, instance_id):
        return self.upload_complete_mocks.pop(0)



class MockRecipeApiClient:
    def __init__(self):
        initial_event_fixture = os.environ.get("EVENT_FIXTURE", None).strip()
        if not initial_event_fixture:
            raise ValueError(
                'Aborting. Test container needs to have an envionment variable of "EVENT_FIXTURE".'
            )
        self.initial_event_fixture = initial_event_fixture

        assert os.environ.get("RECIPE_API_URL", False)

    def get_recipe(self, dataset_id: str):

        if (
            self.initial_event_fixture
            == "opendata-v4-upload-initialiser/events/valid.json"
        ):
            return {"fake_recipe": "USE SOMETHING A TAD MORE REPRESENTATIVE"}

        else:
            raise ValueError(
                f'You are calling MockRecipeApiClient.get_recipe() but no responses for the starting event "{self.initial_event_fixture}" have been defined.'
            )


class MockLambdaClient:
    def __init__(self):
        # Get the name of the start json fixture from an env var. i.e what our test passes in as "event"
        # Example: features/fixtures/opendata-transform-decision-lambda/events/no_bucket_name.json
        initial_event_fixture = os.environ.get("EVENT_FIXTURE", None).strip()
        self.initial_event_fixture = initial_event_fixture
        if not initial_event_fixture:
            raise ValueError(
                'Aborting. Test container needs to have an envionment variable of "EVENT_FIXTURE".'
            )

        # From here, we just use the name of the fixture to decide what mock responses are
        # getting returned.

        # Any test thats meant to fail before you client.invoke() go here - they dont need a mocked response
        # but they DO need to exist so we can throw an error where someone typos or forgets to setup
        # the fixture, otherwise errors of that kind will get obfiscated (i.e this allows the "else" clause).
        if initial_event_fixture in [
            "opendata-transform-decision-lambda/events/no_bucket_name.json",
            "opendata-transform-decision-lambda/events/no_object_key.json",
            "opendata-v4-upload-initialiser/events/no_bucket_name.json",
            "opendata-v4-upload-initialiser/events/not_automated.json",
            "opendata-v4-upload-poller/events/bad-starting-event.json"
        ]:
            self.mock_responses = []

        # For everything else, just return based on the fixture we've passed in
        # If your lambda test invokes once - provide a list of 1
        # If it invokes twice - provide a list of 2
        # etc

        elif (
            initial_event_fixture == "opendata-v4-upload-initialiser/events/valid.json"
        ):
            self.mock_responses = [
                payload(
                    {
                        "body": {
                            "metadata": {},
                            "dimension_data": {},
                            "usage_notes": {},
                        },
                        "statusCode": 200,
                    }
                ),
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
                payload(
                    {
                        "statusCode": 200,
                    }
                ),
            ]
        elif (
            initial_event_fixture
            == "opendata-transform-decision-lambda/events/failed_response_details_lambda.json"
        ):
            self.mock_responses = [payload({"statusCode": 500})]
        elif (
            initial_event_fixture
            == "opendata-v4-upload-poller/events/valid.json"
        ):
            self.mock_responses = [payload({"statusCode": 200})]
        elif (
            initial_event_fixture == "opendata-v4-upload-poller/events/valid-longer-polling.json"):
                self.mock_responses = [
                    payload({"statusCode": 200}),
                    payload({"statusCode": 200}),
                    payload({"statusCode": 200})
                    ]
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
                payload({"body": {"valid": True}, "statusCode": 200})
            ]

        elif (
            initial_event_fixture
            == "opendata-transform-details-lambda/events/failed_response_metadata_validator.json"
        ):
            self.mock_responses = [payload({"statusCode": 500})]

        else:
            raise ValueError(
                f'You are calling MockLambdaClient but no responses for the starting event "{initial_event_fixture}" have been defined.'
            )

    def invoke(self, FunctionName: str, InvocationType: str, Payload: str):
        try:
            mock_response = self.mock_responses.pop(0)
            return mock_response
        except IndexError as err:
            raise IndexError(
                f"Could not find a mock lambda response for {self.initial_event_fixture}, have you defined one self.mock_responses for _every_ invoke in this test?"
            ) from err


class MockS3Client:
    def __init__(self):
        # Get the name of the start json fixture from an env var. i.e what our test passes in as "event"
        # Example: features/fixtures/opendata-transform-decision-lambda/events/no_bucket_name.json
        initial_event_fixture = os.environ.get("EVENT_FIXTURE", None)
        if not initial_event_fixture:
            raise ValueError(
                'Aborting. Test container needs to have an envionment variable of "EVENT_FIXTURE".'
            )
        self.initial_event_fixture = initial_event_fixture

    def download_fileobj(self, bucket: str, zip_file: str, f: FileIO):
        """
        When the test container is built we mount the contents of
        /features/fixtures/zips as /tmp/zips.

        So our mock "download" is just copy a fixture zip to the COMMON_ZIP_PATH,
        where COMMON_ZIP_PATH is where the lambdas expect the data.
        """

        if (
            self.initial_event_fixture
            == "opendata-v4-upload-metadata-parser/events/valid.json"
        ):
            shutil.copy("/tmp/zips/valid1.zip", COMMON_ZIP_PATH)

        else:
            raise ValueError(
                f'You are calling MockS3Client.download_fileobj() but no responsers for the starting event "{self.initial_event_fixture}" have been defined.'
            )

    def head_object(self, Bucket=None, Key=None):

        if (
            self.initial_event_fixture
            == "opendata-v4-upload-initialiser/events/not_automated.json"
        ):
            return json.dumps({})  # if its not automated, our metadata is not set on the object

        elif (
            self.initial_event_fixture
            == "opendata-v4-upload-initialiser/events/valid.json"
        ):
            return json.dumps({"Metadata": {"source": {"bucket": "", "zip_file": "fake_zip.zip"}}})

        else:
            raise ValueError(
                f'You are calling MockS3Client.head_object() but no responsers for the starting event "{self.initial_event_fixture}" have been defined.'
            )
