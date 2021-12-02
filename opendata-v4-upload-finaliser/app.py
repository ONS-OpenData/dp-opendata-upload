import logging
import json
import os

from lambdautils.helpers import (
    log_as_incomplete, 
    log_as_complete, 
    json_validate
)
from lambdautils.mocking import get_dataset_api_client, get_zebedee_client
from lambdautils.schemas import finaliser_payload_schema


def handler(event, context):
    """
    Lambda to finish upload within CMD
    Adds to collection
    Adds metadata
    """

    access_token = os.environ.get("ZEBEDEE_ACCESS_TOKEN", None)
    if not access_token:
        log_as_incomplete()
        msg = "Aborting. Need a zebedee access token."
        logging.error(msg)
        raise ValueError(msg)
    
    json_validate(event, finaliser_payload_schema)

    dataset_api = get_dataset_api_client(access_token)
    zebedee_api = get_zebedee_client()

    collection_name = event["dataset_details"]["collection_name"]
    dataset_id = event["dataset_details"]["dataset_id"]
    edition = event["dataset_details"]["edition_id"]
    metadata_dict = event["metadata"]
    instance_id = event["instance_id"]

    # Create new collection
    zebedee_api.create_collection(collection_name)
    # Return collection_id
    collection_id = zebedee_api.get_collection_id()
    # Updating general metadata
    dataset_api.update_metadata(dataset_id, metadata_dict)
    # Assigning instance a version number
    dataset_api.create_new_version_from_instance(instance_id, edition)
    # Get new version number
    version_number = dataset_api.get_version_number(dataset_id, instance_id)
    # Add landing page to collection
    zebedee_api.add_dataset_to_collection(collection_id, dataset_id)
    # Add new version to collection
    zebedee_api.add_dataset_version_to_collection(collection_id, dataset_id, edition, version_number)
    # Updating dimension metadata
    dataset_api.update_dimensions(dataset_id, instance_id, metadata_dict)

    log_as_complete()



    