import logging
import boto3
import botocore
import json
from subprocess import check_output

SIGNED_URL_EXPIRATION = 300     # The number of seconds that the Signed URL is valid


logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """

    :param event:
    :param context:

    This function will move the files from the temporary bucket to the CDN bucket.
    1. Copy the files to the new bucket
    2. Remove the files from the old bucket
    3. Update database confirming it's on the CDN
    
    """
    
    ###########################################################
    # Extract the relevant variables from the event
    # Note: We aren't taking the "key" here, because that refers
    # to the actual file. We need to take the "folder"
    
    checksum = event['metadata']['checksum']
    fileName = event['filename']
    bucketSource = event['bucket']
    bucketDestination = 'sdmsorigin' # parametrize this!
    dbTable = 'assets' # Parametrize? Use services for this?
    s3 = boto3.resource('s3')
    s3client = boto3.client('s3')
    obucketSource = s3.Bucket(bucketSource)
    obucketDestination = s3.Bucket(bucketDestination)
    
    
    logger.info("Moving the folder '{}' from '{}' to '{}'".format(fileName, bucketSource, bucketDestination))
    

    ###########################################################
    # Perform the copy AND delete. Delete is performed at the
    # same time for performance reasons
    #
    #   S3 has no true concept of a directory, so we can't just
    #   copy the directory. Instead, we need to list each object
    #   that "starts" with the directory prefix. This is the
    #   filename object from the event
    #
    #   The list objects also has a max listing of 1000 objects.
    #   For long video files, we may run the risk of having a 
    #   large amount of objects (e.g., Thumbnails or MBR chunks
    #   To fix this, we must use the pagination offerings
    
    # Note: We may need to change this for videos
    
    moreObjects = True
    foundToken = False
    
    while moreObjects:
        if not foundToken: # If there isn't a token found
            logger.debug("No token")
            response = s3client.list_objects_v2(
                Bucket = bucketSource
                , Prefix = fileName
                #, Delimiter = '/'
            )
        else: # Add in the foundToken
            logger.debug("Token was found")
            response = s3client.list_objects_v2(
                Bucket = bucketSource
                , ContinuationToken = foundToken 
                , Prefix = fileName
                #, Delimiter = '/'
            )
        
        logger.info("Response: {}".format(response))
        for source in response['Contents']:
            logger.info("File being worked on: {}".format(source))
            # copy and delete
            key = source['Key']
            copy_source = {
                'Bucket' : bucketSource,
                'Key' : key
            }
            
            # Copying the file
            # Copying works by specifying an object at the destination bucket
            obj = obucketDestination.Object(key)
            logger.info("Executing the COPY of '{}'".format(key))
            response = obj.copy(copy_source, {'ServerSideEncryption' :'AES256'})
            logger.info("COPY response: {}".format(response))
            
            # Deleting the file. Note we need to use a new object
            obj = obucketSource.Object(key)
            logger.info("Executing the DELETE of '{}'".format(key))
            response = obj.delete()
            logger.info("DELETE response: {}".format(response))
            
        if "NextContinuationToken" in response:
            found_token = response["NextContinuationToken"]
            moreObjects = True
        else:
            moreObjects = False

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dbTable) 
    
     # Checksum is needed to update the table. It has to be a dictionary
    dbKey = {
        'checksum' : checksum
    } 
    updateExpression = 'set File_Location = :d'
            
    expressionValues = {
        ':d' : 'CDN'
    }
    
    logger.info("Updating the File Location to CDN entry for {} in the {} table".format(key, dbTable))
    
    # Note: "Key" must be a dictionary. The key for this is the checksum
    response = table.update_item(
        Key = dbKey,
        UpdateExpression = updateExpression,
        ExpressionAttributeValues = expressionValues,
        ReturnValues = 'NONE'
        )
    
    
    return event
    """
    Generate a signed URL
    :param expires_in:  URL Expiration time in seconds
    :param bucket:
    :param obj:         S3 Key name
    :return:            Signed URL
    """
    s3_cli = boto3.client(  "s3")
    presigned_url = s3_cli.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': obj},
                                                  ExpiresIn=expires_in)
    return presigned_url