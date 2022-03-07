## Purpose
This lambda is called on when no transforming is required, the data in the original zip file is already a v4. 
The lambda unpacks the v4 and uploads it to the publishing bucket via the upload API. It then invokes the opendata-v4-upload-initialiser with an event invocation type.

The lambda is triggered by the opendata-transform-decision-lambda

