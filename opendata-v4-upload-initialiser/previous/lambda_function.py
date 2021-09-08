import json, boto3
from functions import *

s3 = boto3.client("s3")
client = boto3.client("lambda")
def lambda_handler(event, context):
    
    # Get and confirm that we've been triggered by the event of exactly one file being put to the bucket
    records = event.get('Records', None)
    assert len(records) == 1, f'This lambda should be triggered be receiving exactly one record of a file in the bucket being updated. Got {len(records)}'
    record = records[0]
    
    # Get the fields from the event we care about and put in the source_dict
    try:
      bucket = record["s3"]["bucket"]["name"]
    except KeyError:
      raise KeyError(f'Could not find ["s3"]["bucket"]["name"] in Records[0] of event {json.dumps(event, indent=2)}')
    
    try:
      v4_file = record["s3"]["object"]["key"]
    except KeyError:
      raise KeyError(f'Could not find ["s3"]["object"]["key"] in Records[0] of event {json.dumps(event, indent=2)}')
     
    # get metadata from s3 object
    object_response = s3.head_object(Bucket=bucket, Key=v4_file)
    try:
      metadata = object_response['Metadata']['dataset-details'].replace("'", '"') # json.loads only picks ups double quotes
      metadata_dict = json.loads(metadata) 
    except KeyError:
      raise KeyError(f'could not get required "dataset-details" key from s3 object')

    dataset_id = metadata_dict.get("dataset_id", None)
    assert dataset_id, f'could not get required "dataset_id" key from metadata_dict dict {json.dumps(metadata_dict, indent=2)}'
    
    # create the upload_dict - used for the CMD APIs
    # slightly different format to original script - can now only do one at a time
    upload_dict = {
      'dataset_id':dataset_id,
      'bucket':bucket,
      'v4':v4_file,
      'edition':metadata_dict['edition_id'],
      'collection_name':metadata_dict['collection_name'],
      'metadata':metadata_dict['metadata']
    }
    
    Upload_To_Cmd(upload_dict)

    r = client.invoke(
      FunctionName='opendata-v4-upload-poller',
      InvocationType='Event',
      Payload=json.dumps(upload_dict)
      )
      
    
    # as a sanity check - to be removed
    return upload_dict
  