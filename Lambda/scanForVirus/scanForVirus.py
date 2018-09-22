import logging
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
	
	This function scans the incoming "key" for the virus.
    1. NOT IN PLACE YET: Send asset to virus scans
    2. Pend result
    3. If clear. Add the virus scan to the audit logger. Proceed to the next step
    4. If virus found, put into the quarantine bucket
    
    """
    key = event['key']
    bucket = event['bucket']
    qBucket = 'sdmsquarantine'
    
    logger.info("Sending '{}' to virus scan".format(key))
    # This is where we would put in code to scan the virus
    # OPEN QUESTION: Do we put an audit log for sending the file
    resultStatus = "Virus scan not performed at this time"
    logger.info("Virus scan complete: %s" %(resultStatus))
    
    success = True
    
    if success:  

        AUDIT = {}
        AUDIT['user'] = 'System'
        AUDIT['timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S+0000",time.gmtime())
        AUDIT['action'] = 'File scanned for virus'
        AUDIT['notes'] = resultStatus
        
        event['metadata']['Audit'].append(AUDIT)
        return event
    
    else:
        logger.info("Virus found. Moving '{}' to Quarantine bucket '{}'".format(key, qBucket))
        s3 = boto3.resource('s3')
        s3client = boto3.client('s3')
        objBucket = s3.Bucket(bucket)
        objQBucket = s3.Bucket(qBucket)
        response = ""
        
        copy_source = {
            'Bucket' : bucket,
            'Key' : key
        }
        
        # Copying the file
        # Copying works by specifying an object at the destination bucket
        obj = objQBucket.Object(key)
        logger.info("Executing the COPY of '{}'".format(key))
        #response = obj.copy(copy_source, {'ServerSideEncryption' :'AES256'})
        logger.info("COPY response: {}".format(response))
        
        # Deleting the file. Note we need to use a new object
        obj = objBucket.Object(key)
        logger.info("Executing the DELETE of '{}'".format(key))
        #response = obj.delete()
        logger.info("DELETE response: {}".format(response))
        raise VirusScanFail('File has failed virus scan: {}'.format(resultStatus))
        
class VirusScanFail(Exception): pass