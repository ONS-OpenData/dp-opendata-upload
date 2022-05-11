This lambda is triggered by [opendata-v4-upload-initialiser](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-v4-upload-initialiser)

**Actions**
- Downloads and extracts the files from the original zip file uploaded to `opendata-transform-needed-source-bucket`
- Uses the `metadata_handler` key provided in `manifest.json` to call the relevant metadata handler
- The metadata handler will re-format the metadata into a set format that can then be used by the APIs in [opendata-v4-upload-finaliser](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-v4-upload-finaliser)
- Returns the structured metadata
