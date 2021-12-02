import os
import logging
from typing import Tuple

import requests, datetime

from .helpers import log_as_incomplete


class ZebedeeClient:
    """
    Class for interacting with the Zebedee restful api.
    """

    def __init__(self, access_token: str):

        url = os.environ.get("ZEBEDEE_URL", None)
        if not url:
            raise ValueError("Zebedee url must be exported as an environment variable")

        self.url = url
        self.access_token = access_token

    def create_collection(self, collection_name: str):
        """
        Creates a new collection in florence
        """

        self.collection_name = collection_name
        headers = {"Authorization": self.access_token}
        r = requests.post(self.url + "/collection", headers=headers, json={"name": self.collection_name})
        # doesn't return a 200 when completed
        # so use chek_collection_exists
        self.check_collection_exists()

    def check_collection_exists(self):
        """
        Checks to see if a collection exists - used to check a collection is created
        """

        collection_name_for_url = self.collection_name.replace(' ', '').lower()
        headers = {"Authorization": self.access_token}

        r = requests.get(self.url + '/collection/' + collection_name_for_url, headers=headers)
        if r.status_code != 200:
            raise Exception(f"Collection '{self.collection_name}' not created - returned a {r.status_code} error")

    def get_collection_id(self):
        """
        Gets collection_id from newly created collection
        """

        headers = {'X-Florence-Token':self.access_token}
        collection_name_for_url = self.collection_name.replace(' ', '').lower()

        r = requests.get(f"{self.url}/collection/{collection_name_for_url}", headers=headers)

        if r.status_code == 200:
            collection_dict = r.json()
            collection_id = collection_dict['id']
            return collection_id
        else:
            raise Exception(f"Collection '{self.collection_name}' not found - returned a {r.status_code} error")

    def add_dataset_to_collection(self, collection_id: str, dataset_id: str):
        '''
        Adds dataset landing page to collection
        '''

        headers = {'X-Florence-Token':self.access_token}
        dataset_to_collection_url = f"{self.url}/collections/{collection_id}/datasets/{dataset_id}"

        r = requests.put(dataset_to_collection_url, headers=headers, json={"state": "Complete"})
        if r.status_code == 200:
            print(f"{dataset_id} - Dataset landing page added to collection")
        else:
            raise Exception(f"{dataset_id} - Dataset landing page not added to collection - returned a {r.status_code} error")
        
    def add_dataset_version_to_collection(
        self, 
        collection_id: str, 
        dataset_id: str, 
        edition: str, 
        version_number: str
        ):
        '''
        Adds dataset version to collection
        '''

        headers = {'X-Florence-Token':self.access_token}
        dataset_version_to_collection_url = f"{self.url}/collections/{collection_id}/datasets/{dataset_id}/editions/{edition}/versions/{version_number}"
        
        r = requests.put(dataset_version_to_collection_url, headers=headers, json={"state": "Complete"})
        if r.status_code == 200:
            print(f"{dataset_id} - Dataset version '{version_number}' added to collection")
        else:
            raise Exception(f"{dataset_id} - Dataset version '{version_number}' not added to collection - returned a {r.status_code} error")




    


class RecipeApiClient:
    """
    Class for interacting with the recipe api
    """

    def __init__(self, access_token: str):
        self.url = os.environ.get("RECIPE_API_URL", None)
        if not self.url:
            raise ValueError(
                "The recipe api url must be exported as an environment variable"
            )

        # Store all the recipes when we first ask for them, to save us
        # processing/getting more than once.
        self.recipes_cache = None
        self.access_token = access_token

    def get_all_recipes(self) -> (dict):
        """
        Gets all recipes from the recipe api.

        token is an access token as returned by ZebedeeClient().get_access_token()
        """
        if self.recipes_cache:
            return self.recipes_cache

        headers = {"Authorization": self.access_token}
        r = requests.get(self.url + "?limit=1000", headers=headers)

        if r.status_code == 200:
            self.recipes_cache = r.json()
            # TODO - use a scehema to check contents of self.recipes_cache
            return self.recipes_cache
        else:
            log_as_incomplete()
            raise Exception("Recipe API returned a {} error".format(r.status_code))

    def check_recipe_exists(self, dataset_id: str):
        """
        Checks to make sure a recipe exists for dataset_id
        Returns nothing if recipe exists, raise an error if not
        Uses self.get_all_recipes()
        """

        recipe_dict = self.get_all_recipes()
        # TODO - use a scehema to check contents of recipes_dict

        # create a list of all existing dataset ids
        dataset_id_list = []
        for item in recipe_dict["items"]:
            dataset_id_list.append(item["output_instances"][0]["dataset_id"])
        if dataset_id not in dataset_id_list:
            log_as_incomplete()
            raise Exception("Recipe does not exist for {}".format(dataset_id))

    def get_recipe(self, dataset_id: str):
        """
        Returns recipe for specific dataset
        Uses self.get_all_recipes()
        dataset_id is the dataset_id from the recipe
        """
        self.check_recipe_exists(dataset_id)
        recipe_dict = self.get_all_recipes()

        # iterate through recipe api to find correct dataset_id
        for item in recipe_dict["items"]:
            if dataset_id == item["output_instances"][0]["dataset_id"]:
                return item
        else:
            log_as_incomplete()
            raise Exception(f"Unable to find recipe for dataset id {dataset_id}")


class DatasetApiClient:
    def __init__(self, access_token: str, s3_url: str = None):
        self.url = os.environ.get("DATASET_API_URL", None)
        if not self.url:
            raise ValueError(
                "The dataset api url must be exported as an environment variable"
            )
        self.access_token = access_token

        # s3 url not including file name, i.e "https://s3-<REGION>.amazonaws.com/<BUCKET-NAME>"
        self.s3_v4_bucket_url = s3_url

    def get_all_dataset_api_jobs(self) -> (dict):
        """
        Returns whole contents dataset api /jobs endpoint
        """
        dataset_jobs_api_url = "{self.url}/jobs"
        headers = {"Authorization": self.access_token}

        r = requests.get(dataset_jobs_api_url + "?limit=1000", headers=headers)
        if r.status_code == 200:
            whole_dict = r.json()
            total_count = whole_dict["total_count"]
            if total_count <= 1000:
                dataset_jobs_dict = whole_dict["items"]
            elif total_count > 1000:
                number_of_iterations = round(total_count / 1000) + 1
                offset = 0
                dataset_jobs_dict = []
                for i in range(number_of_iterations):
                    new_url = dataset_jobs_api_url + "?limit=1000&offset={}".format(
                        offset
                    )
                    new_dict = requests.get(new_url, headers=headers).json()
                    for item in new_dict["items"]:
                        dataset_jobs_dict.append(item)
                    offset += 1000
            return dataset_jobs_dict
        else:
            log_as_incomplete()
            raise Exception(
                "/dataset/jobs API returned a {} error".format(r.status_code)
            )

    def get_latest_job_info(self) -> (dict):
        """
        Returns latest job id and recipe id and instance id
        Uses Get_Dataset_Jobs_Api()
        """
        dataset_jobs_dict = self.get_all_dataset_api_jobs()
        latest_id = dataset_jobs_dict[-1]["id"]
        recipe_id = dataset_jobs_dict[-1]["recipe"]  # to be used as a quick check
        instance_id = dataset_jobs_dict[-1]["links"]["instances"][0]["id"]
        return latest_id, recipe_id, instance_id

    def post_new_job(self, v4_file, recipe: dict) -> (Tuple[str, str]):
        """
        Creates a new job in the /dataset/jobs API
        Job is created in state 'created'
        """
        if not self.s3_v4_bucket_url:
            log_as_incomplete()
            raise Exception(
                "To call .post_new_job(), you need to instantiate the dataset api client with an S3 url env var."
            )

        headers = {"Authorization": self.access_token}
        s3_url = f"{self.s3_v4_bucket_url}/{v4_file}"

        payload = {
            "recipe": recipe["recipe_id"],
            "state": "created",
            "links": {},
            "files": [{"alias_name": recipe["recipe_alias"], "url": s3_url}],
        }

        r = requests.post(f"{self.url}/jobs", headers=headers, json=payload)
        if r.status_code == 201:
            print("Job created successfully")
        else:
            log_as_incomplete()
            raise Exception(f"Job not created, returning status code: {r.status_code}")

        # return job ID
        job_id, job_recipe_id, job_instance_id = self.get_latest_job_info()

        # quick check to make sure newest job id is the correct one
        if job_recipe_id != recipe["recipe_id"]:
            log_as_incomplete()
            raise Exception(
                f"New job recipe ID ({job_recipe_id}) does not match recipe ID used to create new job ({recipe['recipe_id']})"
            )
        else:
            return job_id, job_instance_id

    def get_job_info(self, job_id: str):
        dataset_jobs_id_url = f"{self.url}/jobs/{job_id}"
        headers = {"Authorization": self.access_token}

        r = requests.get(dataset_jobs_id_url, headers=headers)
        if r.status_code == 200:
            job_info_dict = r.json()
            return job_info_dict
        else:
            log_as_incomplete()
            raise Exception("/dataset/jobs/{job_id} returned error {r.status_code}")

    def update_state_of_job(self, job_id: str):
        """
        Updates state of job from created to submitted
        once submitted import process will begin
        """

        updating_state_of_job_url = f"{self.url}/jobs/{job_id}"
        headers = {"Authorization": self.access_token}

        updating_state_of_job_json = {}
        updating_state_of_job_json["state"] = "submitted"

        # make sure file is in the job before continuing
        job_id_dict = self.get_job_info(job_id)

        if len(job_id_dict["files"]) != 0:
            r = requests.put(
                updating_state_of_job_url,
                headers=headers,
                json=updating_state_of_job_json,
            )
            if r.status_code != 200:
                log_as_incomplete()
                raise Exception("Unable to update job to submitted state")
        else:
            log_as_incomplete()
            raise Exception("Job does not have a v4 file!")

    def upload_complete(self, instance_id: str) -> (bool):
        """
        Checks state of an instance
        Returns Bool
        """
        instance_id_url = f"{self.url}/instances/{instance_id}"
        headers = {"Authorization": self.access_token}

        r = requests.get(instance_id_url, headers=headers)
        if r.status_code != 200:
            raise Exception(
                "{} raised a {} error".format(instance_id_url, r.status_code)
            )

        dataset_instance_dict = r.json()
        # TODO - schema validate the json we're getting back

        job_state = dataset_instance_dict["state"]

        if job_state == "created":
            log_as_incomplete()
            raise Exception(
                'State of instance is "{job_state}", import process has not been triggered'
            )

        elif job_state == "submitted":
            total_inserted_observations = dataset_instance_dict["import_tasks"][
                "import_observations"
            ]["total_inserted_observations"]
            try:
                total_observations = dataset_instance_dict["total_observations"]
            except:
                error_message = dataset_instance_dict["events"][0]["message"]
                log_as_incomplete()
                raise Exception(error_message)
            logging.info("Import process is running")
            logging.info(
                "{} out of {} observations have been imported".format(
                    total_inserted_observations, total_observations
                )
            )

        elif job_state == "completed":
            return True

        return False

    def update_metadata(self, dataset_id: str, metadata_dict: dict):
        """
        Updates general metadata for a dataset
        """

        metadata = metadata_dict["metadata"]
        assert type(metadata) == dict, "metadata['metadata'] must be a dict"

        headers = {'X-Florence-Token':self.access_token}
        dataset_url = f"{self.url}/datasets/{dataset_id}"
        
        r = requests.put(dataset_url, headers=headers, json=metadata)
        if r.status_code != 200:
            print(f"Metadata not updated, returned a {r.status_code} error")
        else:
            print('Metadata updated')

    def create_new_version_from_instance(self, instance_id: str, edition: str):
        '''
        Changes state of an instance to edition-confirmed so that it is assigned a version number
        Requires edition name & release date ("2021-07-08T00:00:00.000Z")
        Will currently just use current date as release date
        '''

        headers = {'X-Florence-Token':self.access_token}
        instance_url = f"{self.url}/instances/{instance_id}"

        current_date = datetime.datetime.now()
        release_date = datetime.datetime.strftime(current_date, '%Y-%m-%dT00:00:00.000Z')

        r = requests.put(instance_url, headers=headers, json={
            'edition':edition, 
            'state':'edition-confirmed', 
            'release_date':release_date
            }
        )

        if r.status_code == 200:
            print('Instance state changed to edition-confirmed')
        else:
            raise Exception(f"Instance state not changed - returned a {r.status_code} error")

    def get_version_number(self, dataset_id: str, instance_id: str):
        '''
        Gets version number of instance ready to be published from /datasets/instances/{instance_id}
        Only when dataset is in a collection or edition-confirmed state
        Used to find the right version for usage notes or to add version to collection
        Returns version number as string
        '''   

        headers = {'X-Florence-Token':self.access_token}
        instance_url = f"{self.url}/instances/{instance_id}"

        r = requests.get(instance_url, headers=headers)
        if r.status_code != 200:
            raise Exception(f"/datasets/{dataset_id}/instances/{instance_id} returned a {r.status_code} error")
            
        instance_dict = r.json()
        version_number = instance_dict['version']
        
        # check to make sure is the right dataset
        assert instance_dict['links']['dataset']['id'] == dataset_id, f"{instance_dict['links']['dataset']['id']} does not match {dataset_id}"
        # check to make sure version number is a number
        assert version_number == int(version_number), f"Version number should be a number - {version_number}"
        
        return str(version_number)

    def update_dimensions(self, dataset_id: str, instance_id: str, metadata_dict: dict):
        '''
        Used to update dimension labels and add descriptions
        '''
        dimension_dict = metadata_dict['dimension_data']
        assert type(dimension_dict) == dict, 'dimension_dict must be a dict'
        
        headers = {'X-Florence-Token':self.access_token}
        instance_url = f"{self.url}/instances/{instance_id}"
        
        for dimension in dimension_dict.keys():
            new_dimension_info = {}
            for key in dimension_dict[dimension].keys():
                new_dimension_info[key] = dimension_dict[dimension][key]
            
            # making the request for each dimension separately
            dimension_url = f"{instance_url}/dimensions/{dimension}"
            r = requests.put(dimension_url, headers=headers, json=new_dimension_info)
            
            if r.status_code != 200:
                print(f"Dimension info not updated for {dimension}, returned a {r.status_code} error")
            else:
                print(f"Dimension updated - {dimension}")

    def update_usage_notes(
        self, 
        dataset_id: str, 
        version_number: str, 
        metadata_dict: dict, 
        edition: str
        ):
        '''
        Adds usage notes to a version - only unpublished
        /datasets/{id}/editions/{edition}/versions/{version}
        usage_notes is a list of dict(s)
        Can do multiple at once and upload will replace any existing ones
        '''        

        if 'usage_notes' not in metadata_dict.keys():
            return 'No usage notes to add'
    
        usage_notes = metadata_dict['usage_notes']
        
        assert type(usage_notes) == list, 'usage notes must be in a list'
        for item in usage_notes:
            for key in item.keys():
                assert key in ('note', 'title'), 'usage note can only have a note and/or a title'
            
        usage_notes_to_add = {}
        usage_notes_to_add['usage_notes'] = usage_notes
        
        headers = {'X-Florence-Token':self.access_token}
        version_url = f"{self.url}/datasets/{dataset_id}/editions/{edition}/versions/{version_number}"
        
        r = requests.put(version_url, headers=headers, json=usage_notes_to_add)
        if r.status_code == 200:
            print('Usage notes added')
        else:
            print(f"Usage notes not added, returned a {r.status_code} error")
            

