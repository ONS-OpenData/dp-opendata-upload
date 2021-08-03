
# dp-opendata-upload

Holding repo for code (principally lambda functions) relating to the automated transform and upload of datasets to the CMD platform.

The general principle is we want to use lambda functions as much as possible as (a) microservice architecture scales incredibly well (b) they're easy to maintain (c) they're easy to write and (d) for our purposes and the scale we're working at they're cheap to the point of free (quite possibly literally free - will see).

The downside of lambdas is the 15 minute timeout, this only applies at the point we're transforming very large non-v4 data into v4 data so we're handling these cases with a fallback (think: an alternate "persistent" transform service) via AWS Fargate.

_A note on Microservices: The term gets thrown around a lot and most "micro" services .. aren't. These are, this idea of having a larger number of littler things is deliberate and best practice re SE design principles (you put the complexity in the architecture not the code - because the architecture doesn't change)._

Infrastructure diagram: [click me](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/documentation/opendatatransformupload.png)


### Components

Lambda (and one lambda wrapped in a container) components we're using.

| Name | Type | Location | Description |
| ---- | ---- | -------- | ----------- |
| opendata-transform-decision-lambda | Lambda | `./lambdas/opendata-transform-decision-lambda` | Per task, gathers details and either sends a message to either `sns-opendata-transform-persistant-topic` or triggers `opendata-transformer-lambda`. |
| opendata-tranformer-lambda | Lambda | '`./lambdas/opendata-tranformer-lambda` | Transform source(s) to v4 files. |
| opendata-transformer-persistent | AWS Fargate | `/containers/opendata-transformer-persistant` | Wraps `opendata-transformer-lambda`'s code in a dockerfile for deployment as CaaS. |
| opendata-transform-details-lambda | Lambda | `./lambdas/opendata-transform-details-lambda` | Given a starting point of  bucket url, gets relevant details required to run the transform/upload process. |
| opendata-v4-upload-initialiser | Lambda | `./lambdas/opendata-v4-upload-initialiser` | Given an s3 url to a v4, beings the upload, goes as far as starting observation importing then triggers `opendata-v4-upload-poller`. |
| opendata-v4-upload-metadata-parser | Lambda | `./lambdas/opendata-v4-upload-metadata-parser` | Given an s3 url to metadata in whatever format, return metadata in expected format to `opendata-v4-upload-initialiser`. |
| opendata-v4-upload-poller | Lambda | `./lambdas/opendata-v4-upload-poller` | Polls the apis, when the observation imports have finished triggers `opendata-v4-upload-finaliser` | 
| opendata-v4-upload-finaliser | Lambda | `./lambdas/opendata-v4-upload-metadata-parser` | Given an s3 url to metadata in whatever format, return metadata in expected format to `opendata-v4-upload-initialiser`. |

### SNS Message Queues

We're also using an AWS **SNS** (simple notification service) queues to trigger the persistant transforms (we really don't want to get into http authentication without a good reason).

For a nice video on queues and why they're great see the first 3-4 minutes of [https://www.cloudamqp.com/blog/microservices-message-queue-video.html](https://www.cloudamqp.com/blog/microservices-message-queue-video.html).

For perspective, "Kafka" is a brand name of a particularly performant queue. The queues built into the AWS platform (like SNS) are easily powerful enough for our purposes here (and dont require their own servers/maintenance).
 
| Name | Description |
| ---- | ----------- |
| sns-opendata-transform-persistent-topic | Holds json messages with the information for triggering dp-tranformer-persistent |

