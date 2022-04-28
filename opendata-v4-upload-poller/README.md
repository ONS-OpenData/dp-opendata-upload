This lambda is triggered by [opendata-v4-upload-initialiser](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-v4-upload-initialiser/README.md). The purpose of the poller is to monitor the upload progress in CMD. Lambdas can only run for a set short time, so the poller will invoke itself if the upper time limit is approached. 

Currently there is no real error message if the upload fails, which would cause the lambda to, in theory, invoke itself forever, because of this a hard upper limit of number of re-invokes is hard coded into the lambda script.

**Actions**
- Checks the "status" of the upload using the `instance_id`
- Starts a loop
- If the status is `complete` the [opendata-v4-upload-finaliser](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/opendata-v4-upload-finaliser/README.md) is invoked.
- Elif the lambda run time is over a set time (`MAXIMUM_POLLING_TIME`), the lambda then invokes another upload-poller lambda and then ends the current one.
- Else the lambda waits a set time (`DELAY_BETWEEN_CHECKS`) and starts the loop over by checking the status of the upload. This is common while the observations are being imported.

**Environment variables**
- ACCESS_TOKEN 
- API_URL
- DELAY_BETWEEN_CHECKS
- MAXIMUM_POLLING_TIME

**VPC**
- Is on a VPC
