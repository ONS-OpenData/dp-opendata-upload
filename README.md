
# dp-opendata-upload

Holding repo for code (principally lambda functions) relating to the automated transform and upload of datasets to the CMD platform.

Initial infrastructure sketch: [click me](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/documentation/opendatatransformupload.png)


### Components

| Name | Type | Location | Description |
| ---- | ---- | -------- | ----------- |
| dp-transform-decision-lambda | Lambda | `./lambdas/dp-transform-decision-lambda` | Per task, gathers details and sends a message to either `sns-opendata-transform-topic` or `sns-opendata-transform-persistent-topic`. |
| dp-tranformer-lambda | Lambda | '`./lambdas/dp-transformer-lambda` | Transform source(s) to v4 files. |
| dp-transformer-persistent | AWS Fargate | `/containers/dp-transformer-persistant` | Wraps `dp-transformer-lambda`'s code in a dockerfile for deployment as CaaS. |
| dp-transform-details-lambda | Lambda | `./lambdas/dp-transform-details-lambda` | Given a starting point of  bucket url, gets relevant details required to run the transform/upload process. |
| dp-v4-automated-upload | Lambda | `./lambdas/dp-v4-automated-upload` | Given an s3 url to a v4, uploads the v4 to cmd. |
| dp-v4-automated-upload-metadata-parser | Lambda | `./lambdas/dp-v4-automated-upload-metadata-parser` | Given an s3 url to metadata in whatever format, return metadata in expected format to `dp-v4-automated-upload`. |

We're also using two SNS queus to trigger the transforms via instructions from earlier lambdas.
 
| Name | Description |
| ---- | ----------- |
| sns-opendata-transform-topic | Holds json messages with the information for triggering dp-tranformer-lambda |
| sns-opendata-transform-persistent-topic | Holds json messages with the information for triggering dp-tranformer-persistent |
