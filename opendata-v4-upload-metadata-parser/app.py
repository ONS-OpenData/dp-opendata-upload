
def handler(event, context):
    """
    Principle lambda event handler.
    """

    # Given a starting event from either:
        # opendata-metadata-validator
        # opendata-v4-upload-initialiser

    # Validate that the event matches the schema "source_bucket_schema"

    # Get the manfiest from the source bucket, use it to:
        # Get the metadata file from the source bucket.
        # Get the correct metadata_handler for the metadata file.

    # Parse the metadata as per the specified handler and validate it against 

    # Return it.