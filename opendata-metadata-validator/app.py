import json

from lambdautils.helpers import log_as_complete


def handler(event, context):
    """
    Principle lambda event handler.
    """

    # Given a starting event from opendata-decision-lambda

    # Validate that starting event

    # Call opendata-v4-upload-metadata-parser

    # If you get a response, validate it.

    # If its valid - return a 200 with payload ({"valid": "True"})
    # If its not - return a 200 with payload ({"valid": "False"})

    # TEMPORARY CODE!
    # we need to actually do the above.

    log_as_complete()
    return {
        "statusCode": 200,
        "body": json.dumps({"valid": True}),
    }
