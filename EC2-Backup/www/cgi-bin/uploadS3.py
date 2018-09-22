#!/usr/bin/python

import os, sys
import boto3
import string
import cgi
import cgitb
import subprocess
import time
import uuid
import urllib
import urllib2

sys.path.insert(0, '/Assets/sharedLibraries')
import logger

import simplejson as json
from os.path import basename, splitext

# ENABLES DEBUG ON WEBPAGE
cgitb.enable()


# Puts all the fields from the webpage
form = cgi.FieldStorage()

#print "Content-Type: text/html"     # HTML is following
#print                               # blank line, end of headers


# Process input
try:
    fileitem = form['asset']
except KeyError:
    print "Upload a file OR ELSE"
    exit()

USER = {}
AUDIT = {}
MA = {}
METADATA = {}
BUFFSIZE = 1024 * 512
# We want to add the user input fields to our own
# All user input fields are prepended with "User_"
# We will NOT submit any blank fields
for f in form:
    if f[:5] == "User_":
        userIn = string.strip(form[f].value)
        if userIn != '':
            USER[f[5:]] = form[f].value # not needed?
            METADATA[f] = form[f].value

BUCKETNAME = "sdmsupload"

s3 = boto3.resource('s3')
bucket = s3.Bucket(BUCKETNAME)

# UUID4 gives us a unique filename
# We need to extract the extension, insert UUID and then re-insert EXT
# This assumes we have a file extension

if fileitem.file:
    base = basename(fileitem.filename) # Gets the file name
    fileName, fileExt = splitext(base) # get the name and extension
    uniqueID = str(uuid.uuid4())

    uniqueFileName = fileName + '_' + uniqueID # The new file
    
    fn = uniqueFileName + fileExt # The final unique file
    
    writefile = '/Assets/upload/' + fn
    with open(writefile, 'wb') as asset:
        chunk = fileitem.file.read(BUFFSIZE)
        while chunk:
            asset.write(chunk)
            chunk = fileitem.file.read(BUFFSIZE)
    
    # write the file to a temp directory
    
    # Create Metadata string. We need to account for the following items:
    # Account, Group, User
    # Audit information: User, IP address, timestamp, action, other notes
    # Any user fields
    
    # Create dictionary of values to pass
    #MA['filename'] = fn
    #MA['Account'] = form['Account'].value
    # Audit will go into a list to form a "table"
    AUDIT['User'] = form['User'].value
    AUDIT['IP_address'] = os.environ['REMOTE_ADDR']
    AUDIT['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S+0000",time.gmtime())
    AUDIT['Action'] = 'File uploaded'
    AUDIT['Notes'] = os.environ['HTTP_USER_AGENT']
    
    METADATA['Account'] = form['Account'].value
    METADATA['Group'] = form['Group'].value
    METADATA['audit_User'] = form['User'].value
    METADATA['audit_IP_address'] = os.environ['REMOTE_ADDR']
    METADATA['audit_Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S+0000",time.gmtime())
    METADATA['audit_Action'] = 'File uploaded'
    METADATA['audit_Notes'] = os.environ['HTTP_USER_AGENT']
    
    # We want to use the unique string created along with the filename to denote the workID
    # We will put the unique identified first because it is always 36 characters, with the file name following
    # The workID can be a MAX of 80 characters, so this will guarantee we have a unique ID
    # (e.g., If we have a very long file name, we will never see any unique names
    
    workID = (uniqueID + '_' + fileName)[:80]
    METADATA['workID'] = workID
    
    # Convert the Audit to a list
    A = []
    A.append(AUDIT)
    
    '''MA['Group']=form['Group'].value
    MA['UserFields'] = USER
    MA['Audit'] = A
    # Turn Body in JSON message
    input=json.dumps(MA)'''

    # Inputs are the WRITTEN file, the KEY for the BUCKET, and other ARGS (Metadata, Encryption)
    # We are going to upload into the bucket as a "folder"
    # This allows for two things:
    # 1. To put any additional files in the "folder"
    # 2. To just move the folder + all contents to the main S3 bucket
    
    key = uniqueFileName + '/' + fn
    
    bucket.upload_file(writefile, key, {'Metadata' : METADATA, 'ServerSideEncryption' :'AES256'})

    # Remove the temporary file
    os.remove(writefile)
    

    #print "Your file has been submitted to the state machine for processing. <br/> Please reference %s in the jobs page." %(workID)
    
    #print "<br/> %s" %(response)
    
    url = 'http://ec2-54-173-241-48.compute-1.amazonaws.com/uploadS3.php'

    print 'Status: 302 Found'
    print 'Location:%s?id=%s' % (url,workID[:80])
    print
    

else:
    print "there is issue"
