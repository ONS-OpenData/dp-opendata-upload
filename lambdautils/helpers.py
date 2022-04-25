from enum import Enum
from genericpath import exists
import json
import logging
import os
from os import listdir
from os.path import isfile, join
import zipfile

from jsonschema import validate, ValidationError

from .schemas import manifest_schema


COMMON_ZIP_PATH = "/tmp/source.zip"
V4_BUCKET_NAME = "ons-dp-develop-publishing-uploaded-datasets"
TRANSFORM_URL = "https://raw.github.com/ONS-OpenData/cmd-transforms/master"


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
    cmd_csvw = "cmd_csvw"



class Source:
    """
    Wrapper for all operations relating to the source zip file.
    Put it all here so we can pull out all the repetative code from
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


def empty_tmp_folder():
    """
    Removes anything in /tmp/
    """
    leftover_files = listdir("/tmp")
    for file in leftover_files:
        if os.path.isdir(f"/tmp/{file}"):
            continue # ignoring macos & pycache
        os.remove(f"/tmp/{file}")
    print("/tmp has been emptied")


def json_validate(data: dict, schema: dict):
    """
    Wrap jsonvalidate to incorporate some logging
    """
    try:
        validate(instance=data, schema=schema)
        print("Schema validated")
    except ValidationError as err:
        log_as_incomplete()
        raise err

def request_id_check(event_dict: dict, response_dict: dict):
    """
    Checks request id from event matches request id from a lambda request response
    """
    event_id = event_dict["request_id"]
    response_id = response_dict["request_id"]
    if event_id != response_id:
        log_as_incomplete()
        raise ValueError(f"aborting, request_id's do not match {event_id}, {response_id}")
    print("request_id's match")

def cmd_csvw_metadata_parser(csv_w: dict):
    """
    converts a csv_w created from CMD into the required metatdata format for the API's
    """
    # Not all fields from the csv_w are included here
    metadata_dict = {}

    # split into 3
    metadata_dict["metadata"] = {}
    metadata_dict["dimension_data"] = {}
    metadata_dict["usage_notes"] = {}

    # currently hacky..
    if "dct:title" in csv_w.keys():
        metadata_dict["metadata"]["title"] = csv_w["dct:title"]
        
    if "dct:description" in csv_w.keys():
        metadata_dict["metadata"]["description"] = csv_w["dct:description"]

    # TODO - more than one contact?
    if "dcat:contactPoint" in csv_w.keys():
        metadata_dict["metadata"]["contacts"] = [{}]
        if "vcard:fn" in csv_w["dcat:contactPoint"][0].keys():
            metadata_dict["metadata"]["contacts"][0]["name"] = csv_w["dcat:contactPoint"][0]["vcard:fn"]
        if "vcard:tel" in csv_w["dcat:contactPoint"][0].keys():
            metadata_dict["metadata"]["contacts"][0]["telephone"] = csv_w["dcat:contactPoint"][0]["vcard:tel"]
        if "vcard:email" in csv_w["dcat:contactPoint"][0].keys():
            metadata_dict["metadata"]["contacts"][0]["email"] = csv_w["dcat:contactPoint"][0]["vcard:email"]

    if "dct:accrualPeriodicity" in csv_w.keys():
        metadata_dict["metadata"]["release_frequency"] = csv_w["dct:accrualPeriodicity"]

    if "tableSchema" in csv_w.keys():
        dimension_metadata = csv_w["tableSchema"]["columns"]
        metadata_dict["dimension_data"] = Dimension_Metadata_From_CSVW(dimension_metadata)
        metadata_dict["metadata"]["unit_of_measure"] = Get_Unit_Of_Measure(dimension_metadata)
    
    if "notes" in csv_w.keys():
        metadata_dict["usage_notes"] = Usage_Notes_From_CSVW(csv_w["notes"])
        
    print("cmd_csvw_metadata_parser completed parsing")
    return metadata_dict

def Dimension_Metadata_From_CSVW(dimension_metadata):
    '''
    Converts dimension metadata from csv-w to usable format for CMD APIs
    Takes in csv_w['tableSchema']['columns'] - is a list
    Returns a dict of dicts
    '''
    assert type(dimension_metadata) == list, "dimension_metadata should be a list"
    
    # first item in list should be observations
    # quick check
    assert dimension_metadata[0]["titles"].lower().startswith("v4_"), "csv_w[tableSchema][columns][0] is not the obs column"

    # number of data marking columns
    number_of_data_markings = int(dimension_metadata[0]["titles"].split("_")[-1])
    
    wanted_dimension_metadata = dimension_metadata[2 + number_of_data_markings::2]
    dimension_metadata_for_cmd = {}
    
    for item in wanted_dimension_metadata:
        name = item["titles"]
        label = item["name"]
        description = item["description"]
        dimension_metadata_for_cmd[name] = {"label": label, "description": description}
        
    return dimension_metadata_for_cmd

def Get_Unit_Of_Measure(dimension_metadata):
    '''
    Pulls unit_of_measure from dimension metadata
    '''
    assert type(dimension_metadata) == list, "dimension_metadata should be a list"
    
    # first item in list should be observations
    # quick check
    assert dimension_metadata[0]["titles"].lower().startswith("v4_"), "csv_w[tableSchema][columns][0] is not the obs column"
    if "name" in dimension_metadata[0].keys():
        unit_of_measure = dimension_metadata[0]["name"]
    else:
        unit_of_measure = ""
    
    return unit_of_measure

def Usage_Notes_From_CSVW(usage_notes):
    '''
    Pulls usage notes from csv-w to usable format for CMD APIs
    Takes in csv_w['notes'] - is a list
    Creates a list of dicts
    '''
    assert type(usage_notes) == list, "usage_notes should be a list"
    
    usage_notes_list = []
    for item in usage_notes:
        single_usage_note = {}
        single_usage_note["title"] = item["type"]
        single_usage_note["note"] = item["body"]
        usage_notes_list.append(single_usage_note)
        
    return usage_notes_list