import logging
import json
import time
import uuid
from os.path import splitext, basename

import boto3

SIGNED_URL_EXPIRATION = 300     # The number of seconds that the Signed URL is valid


logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """

    :param event:
    :param context:

    This function will review the incoming asset and determine what asset class it should be:
    Options include:
        1. Video
        2. Image
        3. Audio
        4. Other -- This is a catch-all
    
    Code performs the following tasks:
        1. Assign extension mappings to VIDEO, AUDIO, or IMAGE 
        2. Extract file extension from the key
        3. Look up the file extension within the mapping table
            a. If there is a match, assign to the lookup value
            b. If there is no match, assign to Other
        4. Add the "assetClass" class to the event and return the function
        
    Future options:
        1. Split out Other into some form of documents
        2. Account level overrides
        3. Remove the hard-coding of asset classes to something more dynamic
        4. Review MIME-Type instead of extension
        
    """
    
    logger.info("Identifying asset class for %s from %s bucket..." %(event['key'],event['bucket']))
    
    EXTS = loadExtensions()
    
    logger.info("Extension Mapping loaded: %s" %EXTS)
    
    # The "key" contains the folder name first, then the file
    # Basename will get us the end file name, and split ext will separate things out
    fileName, fileExt = splitext(basename(event['key']))
    
    logger.info("Identified extension: '%s'" %fileExt)
    
    try:
        assetClass = EXTS[fileExt[1:].lower()]
    except KeyError:
        assetClass = "Other"
        logger.info("Extension was not found in in the mapping")
        
    logger.info("Identified asset class: '%s'" %assetClass)
    
    event['assetClass'] = assetClass
    event['filename'] = fileName
    event['extension'] = fileExt

    return event
        
        
def loadExtensions():
    E = {}
    # Listing of Audio extensions
    Audio = [ \
    'mp3' \
    , 'aiff' \
    ' ,wma' \
    , 'aac' \
    , 'flac' \
    , 'm4a' \
    ]
    
    logger.debug("Audio types %s:" %Audio)
    
    # Listing of video extensions
    Video = [ \
    'ogg' \
    , 'webm' \
    , '3gp' \
    , 'mp4' \
    , 'avi' \
    , '264' \
    , 'mov' \
    , 'mkv' \
    , 'avc' \
    , 'h264' \
    , 'flv' \
    , 'swf' \
    , 'wmv' \
    , 'mxf' \
    , 'mjpeg' \
    , 'mjpg' \
    , 'm4v' \
    , 'mpg' \
    , 'mpeg' \
    , 'h265' \
    , 'asf' \
    , 'vc1' \
    ]
    
    logger.debug("Video types %s:" %Video)
    
    Image = [ \
    'tif' \
    , 'tiff' \
    , 'gif' \
    , 'jpeg' \
    , 'jpg' \
    , 'png' \
    , 'bmp' \
    , 'bpg' \
    , 'jpeg2000' \
    , 'jpg2000' \
    , 'svg' \
    ]
    
    logger.debug("Image types %s:" %Image)
    
    # Load the lists into a full Dictionary
    for i in Image:
        E[i] = "Image"
        
    for a in Audio:
        E[a] = "Audio"
        
    for v in Video:
        E[v] = "Video"
        
    return E

