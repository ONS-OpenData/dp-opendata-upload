This lambda is triggered by either [opendata-source-extractor-lambda](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-source-extractor-lambda/README.md) / [opendata-transformer-lambda](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-transformer-lambda/README.md)

**Actions**
- Invokes [opendata-v4-upload-metadata-parser](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-v4-upload-metadata-parser/README.md) and requests a response
- Starts making API calls to upload the v4 into CMD
- Invokes [opendata-v4-upload-poller](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-v4-upload-poller/README.md) and passes on the metadata returned from the metadata parser

**Environment variables**
- ACCESS_TOKEN 
- API_URL

**VPC**
- Is on a VPC
