The metadata validator is triggered by [opendata-transform-details-lambda](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-transform-details-lambda).

**Actions** 
- Downloads and extracts the files from the original zip file uploaded to `opendata-transform-needed-source-bucket`
- Uses the `metadata_handler` key provided in `manifest.json` to validate the format of the metadata against the relevant metadata handler
- Returns `True` if metadata is in a valid format, `False` if it is not
