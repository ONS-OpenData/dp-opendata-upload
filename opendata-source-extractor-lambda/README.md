This lambda is triggered by [opendata-transform-decision-lambda](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-transform-decision-lambda). This lambda is called on when no transforming is required, the data in the original zip file is already a v4.

**Actions**
- Downloads and extracts the files from the original zip file uploaded to opendata-transform-needed-source-bucket
- The v4 is then uploaded to the publishing s3 bucket via the upload API
- Invokes the [opendata-v4-upload-initialiser](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-v4-upload-initialiser/README.md)

**Environment variables**
- ACCESS_TOKEN 
- API_URL

**VPC**
- Is on a VPC
