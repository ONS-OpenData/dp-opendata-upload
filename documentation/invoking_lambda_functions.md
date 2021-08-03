# Invoking Lambda Functions

There's two distinct variations of this we're gonna be using.

* `Event` - "fire and forget". Start a lambda then carry on execution, dont wait, dont care what happens on/with the invoked lambda (note - does return a status code, could be worth checking).
* `RequestResponse` - "wait for response", a lot like http, invoke the lambda and wait to get a response payload (some json) back.

There's slightly different syntax for each as follows:

_Note on lambdas: "event" is your dict of starting data, "context" is irrelivent for our purposes (tracing etc, not mvp)._ 

## Event

Some code for a lambda function that triggers another lambda by the name of `other-lambda-function` with json paylod of `some_payload`.

```python
import json
import boto3

client = boto3.clieng('lambda')
def lambda_handler(event, context):

  some_payload = {
    "foo" : "bar
  }
    
  client.invoke(
      FunctionName='other-lambda-function',
      InvocationType='Event',
      Payload=json.dumps(some_payload)
  )
```

The result would be `other-lambda-function` is triggered and has `{"foo": "bar"}` in its starting event variable.

## RequestResponse

Some code for a lambda function that triggers another lambda by the name of `another-lambda-function` with json paylod of `some_payload`. In in our example `another-lambda-function` will return a json response of `{"message": "hello world!"}`

```python
import json
import boto3

client = boto3.clieng('lambda')
def lambda_handler(event, context):

  some_payload = {
    "foo" : "bar
  }
    

  response = client.invoke(
      FunctionName='another-lambda-function',
      InvocationType='RequestResponse',
      Payload=json.dumps(some_payload)
  )

  msg = response.get("message")
  print(msg) # This would print hello world.




```

The result would be `another-lambda-function` is triggered and has `{"foo": "bar"}` in its starting event variable.


