import logging
import subprocess
import json
import time
import uuid

import boto3

SIGNED_URL_EXPIRATION = 300     # The number of seconds that the Signed URL is valid


logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """

    :param event:
    :param context:
	
	This function will start the workflow execution. The following processing activities will happen:
	1. Pull the metadata that has been attached
	2. Add a few key pieces of information that can be passed into the workflow
	3. Start the workflow
    """
    # Loop through records provided by S3 Event trigger
    # Note to self: Will there ever be more than one record?
    for s3_record in event['Records']:
        logger.info("Working on new s3_record...")
        # Extract the Key and Bucket names for the asset uploaded to S3
        key = s3_record['s3']['object']['key']
        logger.info(s3_record['s3']['object'])
        bucket = s3_record['s3']['bucket']['name']
        logger.info("Bucket: {} \t Key: {}".format(bucket, key))
        # Generate a signed URL for the uploaded asset
        signed_url = get_signed_url(SIGNED_URL_EXPIRATION, bucket, key)
        logger.info("Signed URL: {}".format(signed_url))

        MA = {}
        AUDIT = {}
        USER = {}

        USER, AUDIT, MA = pullS3metadata(bucket, key)

        MA['UserFields'] = USER
        MA['Audit'] = [] # We are creating the Audit List so we can append to it
        MA['Audit'].append(AUDIT)
        MA['checksum'] = s3_record['s3']['object']['eTag']
        MA['file_size'] = s3_record['s3']['object']['size']

        logger.info(MA)
        workID = MA['workid']

        INPUT = {
            'bucket' : bucket,
            'key': key,
            'metadata' : MA,
        }


        # Set up step function client
        sfn = boto3.client('stepfunctions')
        

        response = sfn.start_execution(
          stateMachineArn='arn:aws:states:us-east-1:835444431888:stateMachine:IngestAsset', # parametrize this
          name=workID,
          input=json.dumps(INPUT)
        )

    return workID[:80]

def get_signed_url(expires_in, bucket, obj):
    """
    Generate a signed URL
    :param expires_in:  URL Expiration time in seconds
    :param bucket:
    :param obj:         S3 Key name
    :return:            Signed URL
    """
    s3_cli = boto3.client("s3")
    presigned_url = s3_cli.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': obj},
                                                  ExpiresIn=expires_in)
    return presigned_url

def pullS3metadata(bucket, key):

    """
    Extract the metadata from the S3 object obtained during upload.
    This includes audit information pulled, user inputted metadata (e.g., description or location, and general account information.
	Additionally, this will create a few
    :param bucket:  S3 bucket name
    :param key:  file key
    :return:            AUDIT dictionary
    :return:            USER dictionary
    :return             GENERAL dictionary
    """

    s3_cli = boto3.client("s3")
    obj = s3_cli.head_object(Bucket=bucket, Key=key)['Metadata']
    
    USER = {}
    AUDIT = {}
    GENERAL = {}
    
    for key in obj:
        # USER fields start with "user_"
        # AUDIT fields start with "audit_"
        # We will remove the prepended items when adding to the larger dictionary
        # All other fields do not have the underscore
        underLocation = key.find('_')
        if underLocation == -1:
            GENERAL[key] = obj[key]
        elif underLocation == 4: # This is a user
            USER[key[5:]] = obj[key]
        elif underLocation == 5: # This is an audit item
            AUDIT[key[6:]] = obj[key]
            
    return USER, AUDIT, GENERAL
     
    
    
# Function is used to standardize naming conventions found in Apple Metadata
# There are two VERY IMPORTANT metadata items in here:
# 1. Creation Date -- This is analogous to the "recorded date" on other devices
# 2. Location ISO 6709 --  This is the geo-location of the file
