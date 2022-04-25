import logging
import json
import os

from lambdautils.helpers import (
    log_as_incomplete, 
    log_as_complete, 
    json_validate
)
from lambdautils.mocking import get_dataset_api_client, get_zebedee_client, get_collection_client
from lambdautils.schemas import upload_finaliser_event_schema


def handler(event, context):
    """
    Lambda to finish upload within CMD
    Adds to collection
    Adds metadata
    """     

    json_validate(event, upload_finaliser_event_schema)

    dataset_api = get_dataset_api_client()
    collection_api = get_collection_client()
    #zebedee_api = get_zebedee_client()

    instance_id = event["instance_id"]
    dataset_id = event["dataset_details"]["dataset_id"]
    edition = event["dataset_details"]["edition_id"]
    collection_name = event["dataset_details"]["collection_name"]
    metadata_dict = event["metadata_dict"]
    
    # Create new collection
    #zebedee_api.create_collection(collection_name)
    collection_api.create_collection(collection_name)
    # Return collection_id
    #collection_id = zebedee_api.get_collection_id()

    # Updating general metadata
    dataset_api.update_metadata(dataset_id, metadata_dict)
    # Assigning instance a version number
    dataset_api.create_new_version_from_instance(instance_id, edition)
    # Get new version number
    version_number = dataset_api.get_version_number(dataset_id, instance_id)
    # Add landing page to collection
    #zebedee_api.add_dataset_to_collection(collection_id, dataset_id)
    collection_api.add_dataset_to_collection(dataset_id)
    # Add new version to collection
    #zebedee_api.add_dataset_version_to_collection(collection_id, dataset_id, edition, version_number)
    collection_api.add_dataset_version_to_collection(dataset_id, edition, version_number)
    # Updating dimension metadata
    dataset_api.update_dimensions(dataset_id, instance_id, metadata_dict)
    # Updating usage notes
    dataset_api.update_usage_notes(dataset_id, version_number, metadata_dict, edition)

    log_as_complete()
    print("Upload complete!")
    return {"body": "Upload Complete!"}



    