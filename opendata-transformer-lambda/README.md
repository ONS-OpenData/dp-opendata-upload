This lambda is triggered by [opendata-transform-decision-lambda](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-transform-decision-lambda/README.md). This lambda is called on when a transform is required.

**Actions**
- Downloads and extracts the files from the original zip file uploaded to opendata-transform-needed-source-bucket
- Invokes the [opendata-transform-retriever](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-transform-retriever/README.md) and requests a response
- Uses the `script` from the response and writes this to `/tmp/transform_script.py` 
- If there any requirement modules in the response these are also written to `/tmp` as `<module>.py`
- Imports the transform script as `transform` and then runs the transform
- The resultant v4 is then uploaded to the publishing s3 bucket via the upload API
- Invokes the [opendata-v4-upload-initialiser](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-v4-upload-initialiser/README.md)
