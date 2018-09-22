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

    This function creates a thumbnail from an image
        1. Generate the signed url
        2. Pull image into temporary directory
        3. Create a thumbnail in the temp directory using ImageMagick (this is built into Lambda)
        4. Upload the thumbnail back to the main S3 directory
        5. Update the database with the thumbnail information
    
    
    Future options:
        1. http://www.imagemagick.org/Usage/thumbnails/ -- Thumbnail optimizations?
        2. Does it make sense to pass images via BASE64 encodings?
        3. Parametrize the "scale"?

        
    """

    scale = "640x360" # Sets the thumbnail size
    bucket = event['bucket']
    key = event['key']
    format = 'png' # Sets the thumbnail format
    
    # Checksum is needed to update the table. It has to be a dictionary
    dbKey = {
        'checksum' : event['metadata']['checksum']
    }        
    
    fileName = event['filename']
    downloadLoc = '/tmp/' + fileName
    outfile = fileName + '_thumbnail.' + format
    
    logger.info("Begin image thumbnail creation from {}".format(key))
    
    # Get the signed URL to download the object
    signed_url = get_signed_url(SIGNED_URL_EXPIRATION, bucket, key)
    logger.info("Signed URL: {}".format(signed_url))
    
    ###########################################################
    # Download the object from S3
    logger.info("Attempting to download '{}' from bucket '{}'".format(key, bucket))
    s3 = boto3.resource('s3')
    file = s3.Object(bucket, key)
    file.download_file(downloadLoc)
    logger.info("File downloaded")
    
    ###########################################################
    # Run the Image Magick command
    cmd = ['convert'
                    , downloadLoc
                    ,'-format', format
                    ,'-thumbnail', scale
                    ,'-auto-orient' # Sets it so the thumbnail matches the image rotation
                    ,'/tmp/' + outfile
                  ]
                  
    logger.info("ImageMagick command: {}".format(cmd))
    output = check_output(cmd)
        
    ###########################################################
    # Update the database with the thumbnail information
    
    updateExpression = 'set thumbnail = :t'
    
    expressionValue = {
        ':t' : '/thumbnails/' + outfile
    }
  
    dbTable = 'assets' # Parametrize? Use services for this?
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(dbTable) 
    
    logger.info("Updating the thumbnail entry for {} in the {} table".format(key, dbTable))
    
    # Note: "Key" must be a dictionary. The key for this is the checksum
    response = table.update_item(
        Key = dbKey,
        UpdateExpression = updateExpression,
        ExpressionAttributeValues = expressionValue,
        ReturnValues = 'NONE'
        )
    
    ###########################################################
    # Upload the thumbnail back to S3
    # Note: use the same S3 object as before
    #
    # The thumbnail key will be "folder/thumbnail_folder/thumbnail_file"
    
    s3_bucket = s3.Bucket(bucket)

    thumbKey = fileName + '/thumbnails/' + outfile
    logger.info('Uploading the thumbnail to "{}" using the following key: {}'.format(bucket, thumbKey))
    s3_bucket.upload_file('/tmp/' + outfile, thumbKey, {'ServerSideEncryption' :'AES256'})

    
    return event

def get_signed_url(expires_in, bucket, obj):
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