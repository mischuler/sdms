import logging
import sys
import string
import time
import decimal
import json
import boto3
import re

from pymediainfo import MediaInfo 
# Using pymedia means several things
# 1. We need to take the pymedia python libraries from "site-packages"
# 2. We need the shared library for mediainfo "libmediainfo". This is found in /usr/lib64 if installed

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


    G, V, A = parseMediaToDict(signed_url) # pass in the URL
    logger.info('General: {} -- Video: {} -- Audio: {}'.format(G,V,A))
    

    
     # Start Constructing Document
    DOC = {}
    DOC['General'] = G
    if len(V) > 0: DOC['Video'] = V 
    if len(A) > 0: DOC['Audio'] = A
    
    
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
    

###############################################################
# Init Mapping is used to standardize some metadata information we find.
# In mediainfo, we standardize naming conventions found in Apple Metadata
# There are two VERY IMPORTANT metadata items in here:
# 1. Creation Date -- This is analogous to the "recorded date" on other devices
# 2. Location ISO 6709 --  This is the geo-location of the file
# *** THIS MAY NEED TO BE UPDATED WITH NEW APPLE RELEASES ***
def initMapping():
    M = {}
    M['comapplequicktimemake'] = "make"
    M['comapplequicktimemodel'] = "model"
    M['comapplequicktimecreationdate'] = "recorded_date"
    M['comapplequicktimesoftware'] = "software"
    M['comapplequicktimelocationiso6709'] = "xyz"
    
    logger.info("Renaming map: {}".format(M))
    return M 
    
def parseMediaToDict(asset):
    
    # Three dictionaries needed
    # General
    # Video
    # Audio
    
    G = {}
    V = {}
    A = {}

    # Setting a few look up lists for the keys
    # DATES are datetime fields we want to make sure are in a consistent format for querying
    # MANUAL_REMOVAL are fields that we don't want in technical metadata, as it reveals internal AWS information
    # MAPPING takes apple specific files and converts them to standard naming conventions
    DATES = ['encoded_date','tagged_date','file_last_modification_date']
    MANUAL_REMOVAL = ['complete_name','folder_name','file_name','file_extension']
    GPS = ['xyz']
    MAPPING = initMapping()

    # Object returned will be separated into tracks -- General, Video, Audio, Video #1...n, Audio #1...n
    # Using "to_data" loads the track information into a dictionary
    # We want to loop through the items and sanitize them
    # NOTE: If there are multiple audio or video tracks, all of them will be overwritten except the last
    # TODO: Identify the number of tracks ahead of time and add each track_id/type to a running dictionary
    
    logger.info('Running the Mediainfo extract')
    MI = MediaInfo.parse(asset, library_file='lib/libmediainfo.so.0')
    for track in MI.tracks:
        logger.info("Track found '{}'".format(track.track_type))
        TRACKDATA = track.to_data()
        trackType =  track.track_type # General, Audio, Video
        for (key,value) in TRACKDATA.items():
            logger.info("Processing key '{}' and value '{}'".format(key,value))
            if key[:5] != 'other': # Don't remember why i had this in here
                # Run the key against the MAPPING Dictionary
                # If it's found, we map the key to an updated value, otherwise we do nothing
                try:
                    key = MAPPING[key]
                except KeyError:
                    pass
                    
                if key in MANUAL_REMOVAL:
                    # skip this value
                    continue

                # If there is a GPS value, we want to add this to the "General Track" 
                # We will break it apart to lat, long, and alt
                # If the values are already found (NOTE: What use case is this?), we don't overwrite
                if key in GPS:
                    latitude, longitude, altitude = parseGPS(value)
                
                    if 'Latitude' not in G:
                        G['Latitude']=latitude
                    
                    if 'Longitude' not in G:
                        G['Longitude']=longitude
                    
                    if altitude != '':
                        if 'Altitude' not in G:
                            G['Altitude']=altitude
                   
                    continue

                #  This helps us convert a date into a consistent UTC value
                if key in DATES:
                    value = parseDate(value)
                    
                # Pick the dictionary to use
                if trackType == 'General':
                    G[key] = value
                elif trackType == 'Video':
                    V[key] = value
                elif trackType == 'Audio':
                    A[key] = value
                '''elif fnmatch.fnmatch(trackType,'Video #*'): # Captures Video1...n
                    try:
                        V[trackType].update({key: value}) # only works if we've added a key.
                    except KeyError:
                        V[trackType] = {key : value}
                elif fnmatch.fnmatch(trackType,'Audio #*'): # Captures Audio1...n
                    try:
                        A[trackType].update({key : value})
                    except KeyError:
                        A[trackType] = {key : value}'''

    return G,V,A

def parseDate(date):

    # Format looks like UTC 2016-02-19 03:42:55
    # This needs to turn into $TIME"T"$DATE+0000

    D = string.split(date)

    newDate = "%sT%s+0000" % (D[1],D[2])
    return newDate

    
#############################
# A helper class to convert the GPS from "xyz" (+35.7942-078.6358+101.768/)
# to separate lat, long, and alt
def parseGPS(gps):
    # Find all +/-
    # If there are only 2 values, then we don't have an altitude value
    # Then, find the end "/"

    plusminus = re.compile("[+-]")
    counter = 0
    # Loop through the GPS to find each plus or minus
    # As we find items, increase the counter
    # Each "i" is an object with a "start" point
    for i in re.finditer(plusminus,gps):
        # If we've already seen, the latitude, find the longitude starting point
        if counter == 1:
            longstart = i.start()
        start = i.start()
        counter = counter + 1

    # if we have 3, we have altitude
    if counter == 3:
        latitude = gps[:longstart] # Goes until  the start of longitude
        longitude = gps[longstart:start] # The last "start" is the altitude index
        altitude = gps[start:len(gps)-1] # The last character is "/", so we must remove
    else:
        latitude = gps[:longstart]
        longitude = gps[longstart:len(gps)-1]
        altitude = ''

    return latitude, longitude, altitude
