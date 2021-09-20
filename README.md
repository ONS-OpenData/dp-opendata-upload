# dp-opendata-upload

Holding repo for code (principally lambda functions) relating to the automated transform and upload of datasets to the CMD platform.
Infrastructure diagram: [click me](https://github.com/ONS-OpenData/dp-opendata-upload/blob/main/documentation/opendatatransformupload.png)

## How it works

All lambdas run on an image created from the `Dockerfile` with variations in files informing each lambda (see lambda sub directories). Python packages per lambda are handled by the relevant `requirements.txt` files.

The `./lambdautils` directory contains python code that is passed into _all_ lambdas functions to factor out repetition.

The `./features` directory contains BDD tests and supporting code.

## Testing

All lambdas have BDD tests run on a dockerfile including the amazon RIE (Runtime Interface Emulator) image. This lets us run a full test suite against each lambda locally.

To run the tests:
* clone this repo and cd into it
* `pipenv run behave`

Example of running a specific feature `pipenv run behave ./features/myfeature.feature`

Example of running a specific scenario `pipenv run behave -n "<scenario name>"`

Where more than one scenario has the same name, combine both techiques.

These tests are _not_ end to end tests. When running tests the boto3 clients are replaced with MockClient(s) that returns hard coded responses. Each feature will pass or fail independently of the others.

_Note: a bit slow for now as container (re)builds on each scenario rather than each feature. Fixable but not urgent._


## Deployment

You'll have to rerun the following setup line from time to time if your token expires, it's pretty painless.


### Setup

First, you'll need to have the ecr url exported via an environment variable `AWS_ECR_URL`.

You register your docker client with your aws cli via:

```
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin $AWS_ECR_URL
```

_Note: I'm not putting the region on github, just look in the console._

### Usage

To update the lambda image on aws to match whats defined in this repo, pass the name of the lambda function to the makefile, example:

```
make lambda=opendata-transform-decision-lambda
```

That'll update the registered image to match whatever you've got locally and deploy it as a lambda.


### Dependencies

The contents of `./lambdautils` is copied into each lambda function as its image is built. It is **not** pip installed (pip install from a git repo requires git, adding git to the lightweight aws lambda image is problematic).

However, `./lambdautils` _is_ setup as an installable package, this is just so that the `pipenv` venv can find it for intellij hinting/dot notaton while developing.

The take away is add what you need, but any packages you utilise in `./lambdautils` need to (a) be included in the aws base image (like boto3) or (b) be added to the `requirements.txt` for the lambda(s) in question.

To update the virtual env (for intellij etc) also add your new package to `install_requires` in `setup.py` then run `pipenv install`.