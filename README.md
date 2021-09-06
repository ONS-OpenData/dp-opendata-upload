# dp-opendata-upload

Holding repo for code (principally lambda functions) relating to the automated transform and upload of datasets to the CMD platform.
Infrastructure diagram: [click me](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/documentation/opendatatransformupload.png)

## How it works

All lambdas run on an image created from the `Dockerfile` with variations in files informing each lambda (see lambda sub directories). Python packages per lambda are handled by the relevant `requirements.txt` files.

The `./common` directory contains python code that is passed into _all_ lambdas functions to factor out repetition.

The `./features` directory contains BDD tests and supporting code.

## Testing

All lambdas have BDD tests run on a dockerfile including the amazon RIE (Runtime Interface Emulator) image. This lets us run a full test suite against each lambda locally.

To run the tests:
* clone this repo and cd into it
* `pipenv run behave`

Example of running a specific feature `pipenv run behave ./features/myfeature.feature`

Example of running a specific scenario `pipenv run behave -n "<scenario name>"`

Where more than one scenario has the same name, combine both techiques.

These tests are _not_ end to end tests. When running tests the boto3 lambda client is replaced with a MockClient that returns hard coded responses. Each feature will pass or fail independently of the others.

_Note: a bit slow for now as the rie container (re)builds on each scenario rather than each feature. Fixable but not urgent._


## Deployment

TODO



