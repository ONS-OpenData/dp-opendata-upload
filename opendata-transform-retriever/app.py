import requests

from lambdautils.helpers import (
    log_as_incomplete,
    log_as_complete,
    TRANSFORM_URL, 
    json_validate
)
from lambdautils.schemas import transform_retriever_event_schema

def handler(event, context):
    """
    Gets the transform script from github as a string
    """
    json_validate(event, transform_retriever_event_schema)
    transform_repo = event["transform"]
    transform_url = f"{TRANSFORM_URL}/{transform_repo}/main.py"

    r = requests.get(transform_url)
    if r.status_code != 200:
        log_as_incomplete()
        raise Exception(f"{transform_url} raised a {r.status_code} error")
    
    script = r.text

    # check to see if there is a requirements.txt file
    # is used if extra python scripts are needed - ie sparsity functions
    requirements_url = f"{TRANSFORM_URL}/{transform_repo}/requirements.txt"
    r = requests.get(requirements_url)
    requirements_dict = {} # will be empty if no requirements needed
    if r.status_code == 200:
        requirements = r.text
        requirements = requirements.strip().split("\n")

        for module in requirements:
            module_url = f"{TRANSFORM_URL}/modules/{module}/module.py"
            module_r = requests.get(module_url)
            if module_r.status_code != 200:
                log_as_incomplete()
                raise Exception(f"{module_url} raised a {module_r.status_code} error")

            module_script = module_r.text
            requirements_dict[module] = module_script


    log_as_complete()
    return {
        "statusCode": 200, 
        "body": script,
        "requirements": requirements_dict,
        "request_id": event["request_id"]
        }