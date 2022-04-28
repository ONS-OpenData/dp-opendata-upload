The details lambda is triggered by the [opendata-transform-decision-lambda](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-transform-decision-lambda/README.md). It also stores a `details.json` file which contains relevant dataset details for the whole pipeline.

**Actions**
- Invokes the [opendata-metadata-validator](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-metadata-validator/README.md) and requests a response
- Uses the `is_valid` response from the validator to continue if `True` or raise an error if `False`
- Opens `details.json` and retrieves the relevant transform details for the given dataset
- Returns the transform details
