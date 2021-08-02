
# dp-opendata-upload

Holding repo for code (principally lambda functions) relating to the automated transform and upload of datasets to the CMD platform.

Initial infrastructure sketch: [click me](https://github.com/ONS-OpenData/dp-opendata-upload/blob/master/documentation/opendatatransformupload.png)


### Components

| Name | Type | Location | Description |
| ---- | ---- | -------- | ----------- |
| dp-transform-decision-lambda | Lambda | `./lambdas/dp-transform-decision-lambda` | Per task, either trigger `dp-transform-lambda` or sends a message to `dp-transform-persistent-queue` uses information from `dp-transform-details-lambda` |
| dp-tranformer-lambda | Lambda | '`./lambdas/dp-transformer-lambda` | Transform source(s) to v4 files.
| dp-transform-persistent-queue | SQS | `./documentation/sqs.md` (documentation only) | Simple queue to hold details of long running transforms that need to be ran. |
| dp-transformer-persistent | AWS Fargate | `/containers/dp-transformer-persistant` | Wraps `dp-transform-lambda` in a dockerfile for deployment as CaaS. |
| dp-transform-details-lambda | Lambda | `./lambdas/dp-transform-details-lambda` | Given a starting point of  bucket url, gets relevant details required to run the transform/upload process. |
dp-v4-automated-upload-decision | Lambda | `./lambdas/dp-v4-automated-upload-decision` | Given an s3 url, decides whether to trigger `dp-v4-automated-upload` or not. |
| dp-v4-automated-upload | Lambda | `./lambdas/dp-v4-automated-upload` | Given an s3 url to a v4, uploads the v4 to cmd. |
| dp-v4-automated-upload-metadata-parser | Lambda | `./lambdas/dp-v4-automated-upload-metadata-parser` | Given an s3 url to metadata in whatever format, return metadata in expected format to `dp-v4-automated-upload`. |
