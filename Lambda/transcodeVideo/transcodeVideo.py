import logging
import boto3
import botocore
import math

SIGNED_URL_EXPIRATION = 300     # The number of seconds that the Signed URL is valid


logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """

    :param event:
    :param context:

    This function runs the video transcoding operations
    1. Invoke the workflow
    2. Wait for the operation to complete
    3. Update the database entry with entries for the thumbnail and PDL
    """
    
    ###########################################################
    # The Pipeline ID must be configured to read from the same bucket
        
    inputKey = event['key'] 
    bucket = event['bucket']
    checksum = event['metadata']['checksum'] # Needed for DB update
    fileName = event['filename']
    duration = event['DOC']['General']['duration'] # Pulls the length of the video in milliseconds
    
    # Compute the output key which will look like:
    # $folderName/converted/$keyWithoutExtension_PDL.mp4
    # Files are put into a "converted" folder
    # We are using an "output prefix" so the first filename is already covered
    outputKey = 'converted/' + fileName + '_PDL.mp4'
 
    client = boto3.client('elastictranscoder')
    waiter = client.get_waiter('job_complete')
    
    
    # pipelneId is testtranscode
    pipelineId = '1517872342212-nq45qn' # This needs to be an environmental variable
    dbTable = 'assets' # Parametrize? Use services for this?
    presetId = '1351620000001-000040'
    thumbnailPattern = 'thumbnails/' + fileName + '_thumbnail_{count}'
    
    # Set up the various pieces of the create job callable
    encryption = {
        'Mode' : 's3'
    }
    
    input = {
        'Key' : inputKey
        , 'FrameRate' : 'auto'
        , 'Resolution' : 'auto'
        , 'AspectRatio' : 'auto'
        , 'Interlaced' : 'auto'
        , 'Container' : 'auto'
    }
    
    output = {
        'Key' : outputKey
        , 'ThumbnailPattern' : thumbnailPattern
        , 'ThumbnailEncryption' : encryption
        , 'Encryption' : encryption
        , 'PresetId' : presetId
    }
    
    logger.info("Submitting job for '{}' using PipelineID '{}' and PresetID '{}'".format(inputKey, pipelineId, presetId)) 

    response = client.create_job(
        PipelineId = pipelineId
        , Input = input
        , Output = output
        , OutputKeyPrefix = fileName + '/'
    )
    logger.info("Submitted job: {}".format(response)) 
    
    #######################################################
    # Job has been submitted, now we need to wait for completion
    jobId = response['Job']['Id']
    

    
    # The delay value is how often we want to poll in seconds
    # We want to scale this delay based upon the length of file, which can be found in the technical metadata input
    # This will also depend on "how fast" AWS transcodes
    # The max number is 120, so we can't set things to be too short
    
    minDelay = 10 # TBD. No idea if this makes sense
    computeDelay = math.trunc((duration / 1000) / 3 ) # Educated guess?
    
    delay = max(minDelay, computeDelay)
    
    logger.info("Begin polling with {} second delay for Job ID: '{}'".format(delay, jobId))    
    waiter.wait(
        Id = jobId,
        WaiterConfig={
            'Delay' : delay,
            'MaxAttempts' : 120
        }
    )
    logger.info("Polling complete for Job ID: '{}'".format(jobId))
    
    ##########################################################
    # After the thumbnails are created, we need to do three things:
    # 1. Identify the thumbnail to be shown for the video
    # 2. NICE-TO-HAVE: Create the storyboard VTT file (https://support.jwplayer.com/customer/portal
    # 3. Update the DB with the information
    # STORYBOARD OLD OPTION? Create the storyboard object which is [http://docs.brightcove.com/en/perform/brightcove-player/guides/thumbnails-plugin.html#collectimages]
 
    # 1. Identifying thumbnail
    # a. We will read the thumbnail folder to identify the number of objects.
    #    This requires calling the list objects until we have no additional tokens
    # b. We will sum the number of thumbnails found
    # c. Then we will taken the "25%" point of the thumbnails
    
    s3 = boto3.resource('s3')
    s3client = boto3.client('s3')
    
    moreObjects = True
    foundToken = False
    thumbnailCount = 0
    thumbnailTiming = .25
    
    while moreObjects:
        if not foundToken: # If there isn't a token found
            logger.debug("No token")
            response = s3client.list_objects_v2(
                Bucket = bucket
                , Prefix = fileName + '/thumbnails/'
                #, Delimiter = '/'
            )
        else: # Add in the foundToken
            logger.debug("Token was found")
            response = s3client.list_objects_v2(
                Bucket = bucket
                , ContinuationToken = foundToken 
                , Prefix = fileName + '/thumbnails/'
                #, Delimiter = '/'
            )
        
        logger.info("Response: {}".format(response))
        thumbnailCount = thumbnailCount + len(response['Contents'])
            
        if "NextContinuationToken" in response:
            found_token = response["NextContinuationToken"]
            moreObjects = True
        else:
            moreObjects = False
            
     
    # Round up so that we don't have a 0 index and truncate to remove trailing decimals, and pad to 5
    index = '%05d' % math.trunc(math.ceil(thumbnailCount * thumbnailTiming))
    logger.info("Number of thumbnails: {}\tIndex identified: {}".format(thumbnailCount, index))

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dbTable) 
    
     # Checksum is needed to update the table. It has to be a dictionary
    dbKey = {
        'checksum' : checksum
    } 
    
    updateExpression = 'set thumbnail = :t, PDL = :p'
    thumbnail = '/thumbnails/%s_thumbnail_%s.png' % (fileName,index)
    PDL = '/' + outputKey
    expressionValues = {
        ':t' : thumbnail
        ,':p' : PDL
    }
    
    logger.info("Updating the thumbnail and PDL for {} in the {} table".format(inputKey, dbTable))
    
    # Note: "Key" must be a dictionary. The key for this is the checksum
    response = table.update_item(
        Key = dbKey,
        UpdateExpression = updateExpression,
        ExpressionAttributeValues = expressionValues,
        ReturnValues = 'NONE'
        )
    
    
    return event
