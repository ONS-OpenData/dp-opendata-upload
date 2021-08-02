
# dp-opendata-upload

Holding repo for code (principally lambda functions) relating to the automated transform and upload of datasets to the CMD platform.

Initial infrastructure sketch: [click me](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/documentation/opendatatransformupload.png)


### Components

Lambda (and one lambda wrapped in a container) components we're using.

| Name | Type | Location | Description |
| ---- | ---- | -------- | ----------- |
| dp-transform-decision-lambda | Lambda | `./lambdas/dp-transform-decision-lambda` | Per task, gathers details and sends a message to either `sns-opendata-transform-topic` or `sns-opendata-transform-persistent-topic`. |
| dp-tranformer-lambda | Lambda | '`./lambdas/dp-transformer-lambda` | Transform source(s) to v4 files. |
| dp-transformer-persistent | AWS Fargate | `/containers/dp-transformer-persistant` | Wraps `dp-transformer-lambda`'s code in a dockerfile for deployment as CaaS. |
| dp-transform-details-lambda | Lambda | `./lambdas/dp-transform-details-lambda` | Given a starting point of  bucket url, gets relevant details required to run the transform/upload process. |
| dp-v4-automated-upload | Lambda | `./lambdas/dp-v4-automated-upload` | Given an s3 url to a v4, uploads the v4 to cmd. |
| dp-v4-automated-upload-metadata-parser | Lambda | `./lambdas/dp-v4-automated-upload-metadata-parser` | Given an s3 url to metadata in whatever format, return metadata in expected format to `dp-v4-automated-upload`. |

### SNS Message Queues

We're also using a few AWS **SNS** (simple notification service) queues to trigger the transforms. This keeps everything scalable and secure by default (we really don't want to get into http authentication without a good reason).

For a nice video on queues and why they're great see the first 3-4 minutes of [https://www.cloudamqp.com/blog/microservices-message-queue-video.html](https://www.cloudamqp.com/blog/microservices-message-queue-video.html).

For perspective, "Kafka" is a brand name of a particularly performant queue. The queues built into the AWS platform (like SNS) are easily powerful enough for our purposes here (and dont require their own servers/maintenance).
 
| Name | Description |
| ---- | ----------- |
| sns-opendata-transform-topic | Holds json messages with the information for triggering dp-tranformer-lambda |
| sns-opendata-transform-persistent-topic | Holds json messages with the information for triggering dp-tranformer-persistent |
| sns-opendata-metadata-request-topic | Message for triggering `dp-v4-automated-upload-metadata-parser` to create metadata `dp-v4-automated-upload` can use |
| sns-opendata-metadata-response-topic | Messages containing the metadata (as json) that 'dp-v4-automated-upload` uses |
