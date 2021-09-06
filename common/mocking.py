from io import BytesIO
import json
import logging


class MockClient:
    """
    Simple wrapper for dot notation access to mocked responses.

    Note: remember to json.dumps() the dicts, this is how they
    the reponses get returned live.
    """

    def __init__(self):
        pass

    def invoke(self, FunctionName: str, InvocationType: str, Payload: str):
        """
        Decide what mocked response to return based on the payload.
        """
        logging.warning("Calling MOCKED lambda client")

        # Use test payload to decide what we're returning
        payload_as_dict = json.loads(Payload)

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
                        "body": json.dumps({"is_valid": "true"}),
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
