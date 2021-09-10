from enum import Enum
from genericpath import exists
import json
import logging
import os

from os import listdir
from os.path import isfile, join

from typing import List, Tuple
import zipfile

from jsonschema import validate, ValidationError
from schemas import manifest_schema

COMMON_ZIP_PATH = "/tmp/source.zip"


class InvocationResult(Enum):
    """
    Enum for logging our the result of running the lambda
    """

    complete = "lambda completed operation"
    incomplete = "lambda failed to complete operation"


def log_as_incomplete():
    """Forced to used warning for now. Pulling this out for when we remedy that"""
    logging.warning(InvocationResult.incomplete.value)


def log_as_complete():
    """Forced to used warning for now. Pulling this out for when we remedy that"""
    logging.warning(InvocationResult.complete.value)


class TransformType(Enum):
    """
    Enum for tracking the different kinds of pipelines in use
    """

    short = "short"
    long = "long"
    none = "none"


class MetadataHandler(Enum):
    """
    Enum for tracking the different kinds of metadata handlers
    """

    correctly_structured = "correctly_structured"


class Source:
    """
    Wrapper for all operations relating to the source zip file.
    Put it all here so we can pull out all the preetative code from
    the lambdas.
    """

    def __init__(self, path_to_zip):
        if not os.path.exists(path_to_zip):
            log_as_incomplete()
            raise FileNotFoundError(f"Cannot find source zip {path_to_zip}")
        with zipfile.ZipFile(path_to_zip, "r") as zip:
            unzip_dir = "/tmp"
            zip.extractall(unzip_dir)

        # Cache, as we'll refer to this a few times
        self.manifest = None

    def assert_exists(self, file_path):
        """
        Check if a file exists
        """
        if not os.path.exists(file_path):
            log_as_incomplete()
            raise FileNotFoundError("The specified file {file_path} does not exist")

    def get_manifest(self) -> (dict):
        """
        Get the contents of the manifest.json from the initial source zip
        """
        if self.manifest:
            return self.manifest

        try:
            with open(f"/tmp/manifest.json") as f:
                self.manifest = json.load(f)
        except Exception as err:
            log_as_incomplete()
            raise err

        json_validate(self.manifest, manifest_schema)
        metadata_file = f'/tmp/{self.manifest["metadata"]}'
        self.assert_exists(metadata_file)

        return self.manifest

    def get_metadata_handler(self) -> (str):
        """
        Get the name of the metadata handler from the manifest.json
        included with the initial source zip.
        """
        manifest = self.get_manifest()
        return manifest["metadata_handler"]

    def get_metadata_file_name(self) -> (str):
        """
        The name of the file representing metadata,
        as taken from the initial source zip.
        """
        manifest = self.get_manifest()
        return manifest["metadata"]

    def get_metadata_file_path(self) -> (str):
        """
        Get the path to where we've extracted the file representing metadata,
        as taken from the initial source zip.
        """
        return f"/tmp/{self.get_metadata_file_name()}"

    def get_data_file_paths(self) -> (list):
        """
        Returns a list of filepaths, each representing a single source
        data file from the initial source zip.

        Ignores:
        * the original zip
        * the manifest.json
        * the metadata file declare by the manfiest json
        * macos operating system files (convenience while developing)
        """
        return [
            f"/tmp/{x}"
            for x in listdir("/tmp")
            if isfile(join("/tmp", x))
            and x != "manifest.json"
            and x != self.get_metadata_file_name()
            and not x.startswith("__")
            and not x == COMMON_ZIP_PATH.split("/")[-1]
        ]


def dataset_name_from_zip_name(zip_name: str) -> (str):
    dataset_name = zip_name.split("/")[-2]  # think: make sure this will always work
    return dataset_name


def json_validate(data: dict, schema: dict):
    """
    Wrap jsonvalidate to incorporate some logging
    """
    try:
        validate(instance=data, schema=schema)
    except ValidationError as err:
        log_as_incomplete()
        raise err
