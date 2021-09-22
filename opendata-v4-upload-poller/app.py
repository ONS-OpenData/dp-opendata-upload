import logging
import json

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    json_validate,
)
from lambdautils.schemas import finaliser_payload_schema


def handler(event, context):
    """
    Principle lambda event handler.
    """

    json_validate(event, finaliser_payload_schema)