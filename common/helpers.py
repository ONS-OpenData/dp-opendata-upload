from enum import Enum
from jsonschema import validate, ValidationError
import logging
from typing import List, Tuple


class InvocationResult(Enum):
    """
    Enum for logging our the result of running the lambda
    """

    complete = "lambda completed operation"
    incomplete = "lambda failed to complete operation"


def log_as_incomplete():
    """Forced to used warning for now. Pulling this out for when we remedy that"""
    logging.warning(InvocationResult.incomplete.value)


def log_as_complete():
    """Forced to used warning for now. Pulling this out for when we remedy that"""
    logging.warning(InvocationResult.complete.value)


class TransformType(Enum):
    """
    Enum for tracking the different kinds of pipelines in use
    """

    short = "short"
    long = "long"
    none = "none"


def dataset_name_from_zip_name(zip_name: str):
    dataset_name = zip_name.split("/")[-2]  # have make sure this will always work
    return dataset_name


def json_validate(data: dict, schema: dict):
    """
    Wrap jsonvalidate to incorporate some logging
    """
    try:
        validate(instance=data, schema=schema)
    except ValidationError as err:
        log_as_incomplete()
        raise err
