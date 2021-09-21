import os
from typing import Tuple

import requests

from .helpers import log_as_incomplete


class ZebedeeClient:
    """
    Class for interacting with the Zebedee restful api.
    """

    def __init__(self):

        email = os.environ.get("ZEBEDEE_EMAIL", None)
        if not email:
            raise ValueError(
                "Zebedee login email must be exported as an environment variable"
            )

        password = os.environ.get("ZEBEDEE_PASSWORD", None)
        if not password:
            raise ValueError(
                "Zebedee password must be exported as an environment variable"
            )

        url = os.environ.get("ZEBEDEE_URL", None)
        if not url:
            raise ValueError("Zebedee url must be exported as an environment variable")

        self.email = email
        self.password = password
        self.url = url

    def get_access_token(self) -> (str):

        payload = {"email": self.email, "password": self.password}

        r = requests.post(self.url, json=payload, verify=False)
        if r.status_code == 200:
            access_token = r.text.strip('"')
            return access_token
        else:
            log_as_incomplete()
            raise Exception(
                "Token not created, returned a {} error".format(r.status_code)
            )


class RecipeApiClient:
    """
    Class for interacting with the recipe api
    """

    def __init__(self):
        self.url = os.environ.get("RECIPE_API_URL", None)
        if not self.url:
            raise ValueError(
                "The recipe api url must be exported as an environment variable"
            )

        # Store all the recipes when we first ask for them, to save us
        # processing/getting more than once.
        self.recipes_cache = None

    def get_all_recipes(self, access_token: str) -> (dict):
        """
        Gets all recipes from the recipe api.

        token is an access token as returned by ZebedeeClient().get_access_token()
        """
        if self.recipes_cache:
            return self.recipes_cache

        headers = {"X-Florence-Token": access_token}
        r = requests.get(self.url + "?limit=1000", headers=headers)

        if r.status_code == 200:
            self.recipes_cache = r.json()
            # TODO - use a scehema to check contents of self.recipes_cache
            return self.recipes_cache
        else:
            log_as_incomplete()
            raise Exception("Recipe API returned a {} error".format(r.status_code))

    def check_recipe_exists(self, access_token: str, dataset_id: str):
        """
        Checks to make sure a recipe exists for dataset_id
        Returns nothing if recipe exists, raise an error if not
        Uses self.get_all_recipes()
        """

        recipe_dict = self.get_all_recipes(access_token)
        # TODO - use a scehema to check contents of recipes_dict

        # create a list of all existing dataset ids
        dataset_id_list = []
        for item in recipe_dict["items"]:
            dataset_id_list.append(item["output_instances"][0]["dataset_id"])
        if dataset_id not in dataset_id_list:
            log_as_incomplete()
            raise Exception("Recipe does not exist for {}".format(dataset_id))

    def get_recipe(self, access_token: str, dataset_id: str):
        """
        Returns recipe for specific dataset
        Uses self.get_all_recipes()
        dataset_id is the dataset_id from the recipe
        """
        self.check_recipe_exists(access_token, dataset_id)
        recipe_dict = self.get_all_recipes(access_token)

        # iterate through recipe api to find correct dataset_id
        for item in recipe_dict["items"]:
            if dataset_id == item["output_instances"][0]["dataset_id"]:
                return item
        else:
            log_as_incomplete()
            raise Exception(f"Unable to find recipe for dataset id {dataset_id}")


class DatasetApiClient:
    def __init__(self):
        self.url = os.environ.get("DATASET_API_URL", None)
        if not self.url:
            raise ValueError(
                "The dataset api url must be exported as an environment variable"
            )

        # s3 url not including file name, i.e "https://s3-<REGION>.amazonaws.com/<BUCKET-NAME>"
        self.s3_v4_bucket_url = os.environ.get("S3_V4_BUCKET_URL", None)
        if not self.s3_v4_bucket_url:
            raise ValueError(
                "The s3 v4 bucket url url must be exported as an environment variable"
            )

    def get_all_dataset_api_jobs(self, access_token: str) -> (dict):
        """
        Returns whole contents dataset api /jobs endpoint
        """
        dataset_jobs_api_url = "{self.url}/jobs"
        headers = {"X-Florence-Token": access_token}

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

    def get_latest_job_info(self, access_token: str) -> (dict):
        """
        Returns latest job id and recipe id and instance id
        Uses Get_Dataset_Jobs_Api()
        """
        dataset_jobs_dict = self.get_all_dataset_api_jobs(access_token)
        latest_id = dataset_jobs_dict[-1]["id"]
        recipe_id = dataset_jobs_dict[-1]["recipe"]  # to be used as a quick check
        instance_id = dataset_jobs_dict[-1]["links"]["instances"][0]["id"]
        return latest_id, recipe_id, instance_id

    def post_new_job(
        self, access_token: str, v4_file, recipe: dict
    ) -> (Tuple[str, str]):
        """
        Creates a new job in the /dataset/jobs API
        Job is created in state 'created'
        """
        headers = {"X-Florence-Token": access_token}
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
        job_id, job_recipe_id, job_instance_id = self.get_latest_job_info(access_token)

        # quick check to make sure newest job id is the correct one
        if job_recipe_id != recipe["recipe_id"]:
            log_as_incomplete()
            raise Exception(
                f"New job recipe ID ({job_recipe_id}) does not match recipe ID used to create new job ({recipe['recipe_id']})"
            )
        else:
            return job_id, job_instance_id

    def get_job_info(self, access_token: str, job_id: str):
        dataset_jobs_id_url = f"{self.url}jobs/{job_id}"
        headers = {"X-Florence-Token": access_token}

        r = requests.get(dataset_jobs_id_url, headers=headers)
        if r.status_code == 200:
            job_info_dict = r.json()
            return job_info_dict
        else:
            log_as_incomplete()
            raise Exception("/dataset/jobs/{job_id} returned error {r.status_code}")

    def update_state_of_job(self, access_token: str, job_id: str):
        """
        Updates state of job from created to submitted
        once submitted import process will begin
        """

        updating_state_of_job_url = f"{self.url}jobs/{job_id}"
        headers = {"X-Florence-Token": access_token}

        updating_state_of_job_json = {}
        updating_state_of_job_json["state"] = "submitted"

        # make sure file is in the job before continuing
        job_id_dict = self.get_job_info(access_token, job_id)

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
