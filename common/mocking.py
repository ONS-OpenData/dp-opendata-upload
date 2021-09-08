from io import BytesIO
import json
import logging


class MockS3Client:
    """
    Simple mock s4 client
    """

    def __init__(self):
        logging.info("Using MOCKED s3 client")

    def head_object(self, Bucket=None, Key=None):

        assert Bucket, 'Mock s3 method required both the Bucket and Key kwargs'
        assert Key, 'Mock s3 method required both the Bucket and Key kwargs'
        
        if Key == "dataset-work-all-the-way-through/example.zip":
            return {
                "Metadata": {
                    "source": {
                        "zip_file": "source-from-mock-s3-thats-valid/example.zip",
                        "bucket": "irrelevant"
                    }
                }
            }
        elif Key == "dataset-dont-auto-upload/example.zip":
            return {}
        else:
            raise Exception(f'Couldnt find a mock reponse for Bucket {Bucket}, Key {Key}')

class MockLambdaClient:
    """
    Simple mock lambda client.

    Note: remember to json.dumps() the dicts, this is how
    the reponses get returned live.
    """

    def __init__(self):
        logging.info("Using MOCKED lambda client")

    def invoke(self, FunctionName: str, InvocationType: str, Payload: str):
        """
        Decide what mocked response to return based on the payload.
        """

        payload_as_dict = json.loads(Payload)

        if FunctionName == "opendata-v4-upload-metadata-parser":

            if (
                payload_as_dict["zip_file"]
                == "source-from-mock-s3-thats-valid/example.zip"
            ):
                payload = json.dumps(
                        {
                            "body": json.dumps(
                                {
                                    "metadata": {},
                                    "dimension_data": {},
                                    "usage_notes": {}
                                }
                            ),
                            "statusCode": 200,
                        }
                    )
                return {
                        "Payload": BytesIO(initial_bytes=bytes(payload, encoding="utf-8"))
                    }

        if FunctionName == "opendata-transformer-lambda":

            # Succesful completion from details lambda test
            if (
                payload_as_dict["collection_name"]
                == "fake collection details lambda test"
            ):
                return

        if FunctionName == "opendata-transform-details-lambda":

            if payload_as_dict["zip_file"] == "dataset1/sample.zip":
                payload = json.dumps(
                    {
                        "body": json.dumps(
                            {
                                "transform_details": {
                                    "transform": "url to transform",
                                    "collection_id": "1",
                                    "transform_type": "short",
                                    "dataset_id": "1",
                                    "edition_id": "1",
                                    "collection_name": "fake collection details lambda test",
                                }
                            }
                        ),
                        "statusCode": 200,
                    }
                )
                return {
                    "Payload": BytesIO(initial_bytes=bytes(payload, encoding="utf-8"))
                }

            elif payload_as_dict["zip_file"].startswith("500"):
                payload = json.dumps({"statusCode": 500})
                return {
                    "Payload": BytesIO(initial_bytes=bytes(payload, encoding="utf-8"))
                }

            else:
                raise Exception(
                    'Your mock client is calling "opendata-transform-details-lambda" but no mocked response can be identified.'
                )

        if FunctionName == "opendata-metadata-validator":

            if payload_as_dict["bucket"] == "fake bucket for valid message test":
                payload = json.dumps(
                    {
                        "body": json.dumps({"valid": "True"}),
                        "statusCode": 200,
                    }
                )
                return {
                    "Payload": BytesIO(initial_bytes=bytes(payload, encoding="utf-8"))
                }

            elif payload_as_dict["bucket"] == "fake bucket for 500 response test":
                payload = json.dumps({"statusCode": 500})
                return {
                    "Payload": BytesIO(initial_bytes=bytes(payload, encoding="utf-8"))
                }
            else:
                raise Exception(
                    'Your mock client is calling "opendata-transform-details-lambda" but no mocked response can be identified.'
                )

        else:
            raise Exception(f"No mock client responses exist for {FunctionName}")
