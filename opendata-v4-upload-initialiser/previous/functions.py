# TODO - will these will live in github?
# will require requests module which lambda does not store
# functions are incomplete - only return what we would expect

import time


def Upload_To_Cmd(upload_dict):
    """
    Uploads data into CMD
    Creates new job, attaches s3_url and changes stae of job
    """

    # Quick check on upload_dict format
    Check_Upload_Dict(upload_dict)

    # using service token
    service_token = "<service_token>"

    # setting out variables
    bucket = upload_dict["bucket"]
    v4 = upload_dict["v4"]
    dataset_id = upload_dict["dataset_id"]

    # quick check to make sure recipe exists in API
    Check_Recipe_Exists(dataset_id)

    # v4 already in bucket - does it need moving or can CMD access this bucket
    s3_url = f"https://s3-eu-west-1.amazonaws.com/{bucket}/{v4}"

    # create new job
    job_id, instance_id = Post_New_Job(dataset_id, s3_url)

    # update state of job
    Update_State_Of_Job(job_id)

    # updating some variables
    upload_dict["s3_url"] = s3_url
    upload_dict["job_id"] = job_id
    upload_dict["instance_id"] = instance_id

    # small wait between uploads
    time.sleep(2)


def Check_Upload_Dict(upload_dict):
    """
    Checks upload_dict is in the correct format
    """
    assert type(upload_dict) == dict, "upload_dict must be a dict"

    for key in ("v4", "edition", "collection_name", "metadata", "dataset_id"):
        assert key in upload_dict.keys(), f'upload_dict must have key - "{key}"'


def Check_Recipe_Exists(dataset_id):
    print("Recipe exists")


def Post_New_Job(dataset_id, s3_url):
    # will make post request to /dataset/jobs
    job_id = "job_id"
    instance_id = "instance_id"
    return job_id, instance_id


def Update_State_Of_Job(job_id):
    # will make put request to /dataset/jobs
    print("State updated successfully")
