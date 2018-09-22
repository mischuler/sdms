import logging
import sys
from subprocess import check_output, PIPE
import subprocess
import json
import string
import time
import decimal

import boto3

SIGNED_URL_EXPIRATION = 300     # The number of seconds that the Signed URL is valid


logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """

    :param event:
    :param context:

    This function will perform two key tasks:
        1. Get a "Signed" URL of the S3 file
        1. Extract the Metadata from an image using Exif Tool using the URL
        2. Format key metadata fields and return the updated document
        
    """
    # Generate a signed URL for the uploaded asset
    signed_url = get_signed_url(SIGNED_URL_EXPIRATION, event['bucket'], event['key'])
    logger.info("Signed URL: {}".format(signed_url))

    # Note: We need to us the './' in front of exiftool to make it execute
    # Also, make SURE the permissions are set for 777 on the exiftool
    # -j is used for JSON
    # -d formats the dates into standard UTC
    # -c formats the GPS to decimal
    # -fast is to only use as little data as possible to pull the metadata
    # The last "-" is because of the piping
    cmd1 = ['curl','-s',signed_url]
    cmd2 = ['./exiftool','-fast','-j','-d','"%Y-%m-%dT%H:%M:%S+0000"','-c','"%+.8f"','-']

    logger.info("Exif Tool command is: %s" %cmd2)
    
    p1 = subprocess.Popen(cmd1,stdout=PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p1.stdout, stdout=PIPE)
    p1.stdout.close()
    output = p2.communicate()[0]
    
    logger.info("Exif Tool output: {}".format(output))
    G, I = parseMediaToDict(output)
    logger.info('{} -- {}'.format(G,I))
    
    """
    This is an unsecure version of running the command
    cmd = 'curl -s "{0}" | ./exiftool -fast -j -d "%Y-%m-%dT%H:%M:%S+0000" -c "%+.8f" -'.format(signed_url)
    logger.info('Executed command: "{}"'.format(cmd))
    #cmd = './exiftool'
    output = subprocess.check_output(cmd, shell=True)"""
    
     # Start Constructing Document
    DOC = {}
    DOC['General'] = G
    DOC['Image'] = I

    event['DOC'] = DOC
    
    return event
        
        
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
    
    
def initMapping():

    # This function is used to "rename" fields to be consistent across MediaInfo and ExifTool
    # This will also place the items in the "General" track
    # Longitude
    # Latitude
    # Altitude
    # Make
    # Model
    # Recorded date (DateTimeoriginal)
    # Filesize

    M = {}

    M['GPSLatitude'] = 'Latitude'
    M['GPSAltitude'] = 'Altitude'
    M['GPSLongitude'] = 'Longitude'
    M['Make'] = 'make'
    M['Model'] = 'model'
    M['Software'] = 'software'
    M['GPSDateTime'] = 'recorded_date'
    #M['DateTimeOriginal'] = 'Recorded date' # This field is not 100% accurate
    M['FileSize'] = 'file_size'

    logger.info("Renaming map: {}".format(M))
    return M

def parseMediaToDict(info):

    # Two dictionaries needed
    # General
    # Image

    # File is loaded as a JSON
    # We will take all entries with the exception of the embedded BINARY thumbnail
    # FILE CAN BE LOADED AS A JSON
    # Assume everything is in image with the exception of the following
   
    G = {}
    I = {}

    MAPPING = initMapping()

    I = json.loads(info, parse_float=decimal.Decimal)[0]


    # Altitude information comes back with string information
    # This will adjust the Altitude to a pure number
    # If no altitude is present, skip this
    try:
        I['GPSAltitude'] = string.split(I['GPSAltitude']," ")[0]
    except KeyError:
        pass

    # Remove Thumbail
    I.pop("ThumbnailImage",None)

    # The JSON returned data has quotes around keys. This will parse them out
    for (k,v) in I.items():
        try:
            I[k] = v.replace('"','')
        except AttributeError:
            continue

    # There are certain fields we want consistently mapped across images and videos that are defined in the MAPPING dict
    # This will assign those fields to the General track, and leave the remaining fields
    for (k,v) in MAPPING.items():
        try:
            G[v] = I[k]
            I.pop(k)
        except KeyError:
            continue

    # If we don't get a GPS date, use the Original date
    # Otherwise, we don't have any recorded date present
    try:
        if 'recorded_date' not in G:
            G['recorded_date'] = I['DateTimeOriginal']
    except KeyError:
        pass

    logger.info("I: {}".format(I))
    logger.info("G: {}".format(G))
    return G,I
