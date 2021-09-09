""" Generic steps for all features relating to to lambda evocations """

import json
import logging
import os
from pathlib import Path
from docker import tls
from docker.api import network

import requests
from requests import Response

import docker
from docker import DockerClient
from docker.models.containers import Container

this_dir: Path = Path(os.path.dirname(os.path.realpath(__file__)))
fixture_dir = Path(this_dir.parent / "fixtures")

if not fixture_dir.exists():
    raise FileExistsError("Cannot find fixture directory, aborting.")


def output_container_logs(context):
    """
    Helper to output container logs.
    """
    for log_line in (
        context.test_container.logs(timestamps=True).decode("utf-8").split("\n")
    ):
        logging.info(f"<docker>: {log_line}")


def start_rie(context, lambda_name: str, event_fixture: Path):
    """
    Build and run image using aws lambda Runtime Interface Emulator
    """
    from docker import DockerClient
    from docker.client import DockerClient

    client: DockerClient = (
        docker.from_env()
    )  # DockerClient(base_url='unix://var/run/docker.sock', version='auto', tls=True)

    # docker.from_env()

    client.images.build(
        path=str(this_dir.parent.parent.resolve()),
        buildargs={"LAMBDA_NAME": lambda_name},
        tag="lambda/testing",
        rm=True,
    )
    test_container: Container = client.containers.run(
        "lambda/testing",
        ports={8080: 9000, 3333: 3333},
        publish_all_ports=True,
        environment={"IS_TEST": True, "EVENT_FIXTURE": event_fixture},
        detach=True,
        network_mode="bridge",
        volumes={Path(fixture_dir / "zips"): {"bind": "/tmp/zips/", "mode": "rw"}},
    )

    # TODO: poll for it to start up, not just wait and hope!
    import time

    time.sleep(10)

    context.test_container = test_container


@given('the lambda "{lambda_name}"')
def step_impl(context, lambda_name):
    """
    Specify which lambda we are testing
    """
    context.lambda_name = lambda_name


@given('we specify the event fixture "{sample_fixture}"')
def step_impl(context, sample_fixture):
    """
    Load the event into a python dict as context.sample
    """
    event_fixture = f"{context.lambda_name}/events/{sample_fixture}.json"
    with open(Path(fixture_dir / event_fixture)) as f:
        sample = json.load(f)
    context.sample = sample
    context.event_fixture = event_fixture


@given("we envoke the lambda")
def step_impl(context):
    """
    Post the dict as json to the emulated lambda
    """
    start_rie(context, context.lambda_name, context.event_fixture)
    r: Response = requests.post(
        "http://localhost:9000/2015-03-31/functions/function/invocations",
        json=context.sample,
    )
    assert (
        r.ok
    ), f"Post to lambda failed, response {r.text} with status code {r.status_code}"
    context.response = r


@then("a log line should contain")
def step_impl(context):
    log_lines = context.test_container.logs(timestamps=True).decode("utf-8").split("\n")

    for row in context.table:
        level = f"[{row['level']}]"
        text = row["text"]
        found = False
        for log_line in log_lines:
            if level in log_line and text in log_line:
                found = True

        if not found:
            output_container_logs(context)
            raise AssertionError(
                f'Could not find a log line contains both "{level}" and "{text}" in logs.'
            )


@then("no warning or error logs should occur")
def step_impl(context):
    log_lines = context.test_container.logs(timestamps=True).decode("utf-8").split("\n")
    found = False
    for log_line in log_lines:
        if "[WARNING]" in log_line:
            found == True
        if "[ERROR]" in log_line:
            found = True

    if found:
        output_container_logs(context)
        raise AssertionError(
            f"Found at least one instance of [WARNING] or [ERROR] logs"
        )


@then("the response returned should match")
def step_impl(context):
    r_json_as_str = json.dumps(context.response.json())
    assert (
        r_json_as_str == context.text
    ), f"""
    
    Expected:
    {context.text}

    Got:
    {r_json_as_str}
    """
