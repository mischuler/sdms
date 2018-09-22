# -*- coding: utf-8 -*-

import string
import re
import googlemaps
import sys
import hashlib
import os
import simplejson as json
import decimal


def loadConfig():
    with open('location_config.ini') as configs:
        CONFIG = json.load(configs)
        
    return CONFIG

def computeChecksum(asset):
    # Compute sha1checksum
    
    BUF_SIZE = 1048576
    h = hashlib.sha1()
    with open(asset, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            h.update(data)
    
    return h.hexdigest()

    #cmd = ['sha1sum',asset]
    #return subprocess.check_output(cmd).split()[0]



# method to put in some mappings
def initMapping():
    M = {}
    M['com.apple.quicktime.make'] = "Make"
    M['com.apple.quicktime.model'] = "Model"
    M['com.apple.quicktime.creationdate'] = "Recorded date"
    M['com.apple.quicktime.software'] = "Software"
    M['com.apple.quicktime.location.ISO6709'] = "©xyz"

    return M

def parseGPS(gps):
    # Find all +/-
    # if two, no altitude
    # Find the end "/"

    plusminus = re.compile("[+-]")
    counter = 0
    for i in re.finditer(plusminus,gps):
        if counter == 1:
            longstart = i.start()
        start = i.start()
        counter = counter + 1 
    
    # if we have 3, we have altitude
    if counter == 3:
        latitude = gps[:longstart]
        longitude = gps[longstart:start]
        altitude = gps[start:len(gps)-1]
    else:
        latitude = gps[:longstart]
        longitude = gps[longstart:len(gps)-1]
        altitude = ''

    return latitude, longitude, altitude

def reverseLookup(latitude, longitude):
    
    gmaps = googlemaps.Client(key='AIzaSyASc8ExetKga4u1ZDHBs4-VxUwjgbHzu1U')
    
    address = gmaps.reverse_geocode((latitude, longitude))
    return address


def parseDate(date):

    # Format looks like UTC 2016-02-19 03:42:55
    # This needs to turn into $TIME"T"$DATE+0000

    D = string.split(date)
    
    newDate = "%sT%s+0000" % (D[1],D[2])
    return newDate

# Function will take in a filepath (e.g. /Asset/upload/$filename.$ext) and return
# File name without extension
# File extension (with the ".")
# File path
def splitFilename(fullPath):
    (fileNameAndPath, fileExt) = os.path.splitext(fullPath)
    lastSlash = fileNameAndPath.rfind('/') + 1 # Shift the index by one
    fileName = fileNameAndPath[lastSlash:]
    filePath = fileNameAndPath[:lastSlash]

    return filePath, fileName, fileExt
    

def createDir(path, folder):
    
    newDir = path + folder
    if not os.path.isdir(newDir):
        os.makedirs(newDir)

    return newDir
    
# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)