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

# Set up step function client
sfn = boto3.client('stepfunctions')
    
USER = {}
AUDIT = {}
# We want to add the user input fields to our own
# All user input fields are prepended with "User_"
# We will NOT submit any blank fields
for f in form:
    if f[:5] == "User_":
        userIn = string.strip(form[f].value)
        if userIn != '':
            USER[f[5:]] = form[f].value

# Set directory to upload into
# Maybe this should be a profile config?
upload_dir="/Assets/upload/"

MA = {}
BUFFSIZE = 1024 * 512

# UUID4 gives us a unique filename
# We need to extract the extension, insert UUID and then re-insert EXT
# This assumes we have a file extension

if fileitem.file:
    base = os.path.basename(fileitem.filename)
    NOEXT = base[:base.rfind('.')]
    EXT = base[base.rfind('.'):]
    unique = str(uuid.uuid4())
    fn = NOEXT + '_' + unique + EXT
    logger.log('I','action="Writing file",value="%s"' % fn) 

    # Create a directory for the uploaded file to be contained
    upload_dir = upload_dir + NOEXT + '_' + unique + '/'
    try:
        os.makedirs(upload_dir)
    except OSError:
        logger.log('E','action="Error in creating directory",value="%s"' % OSError) 
    #open(upload_dir + fn, 'wb').write(fileitem.file.read())
    with open(upload_dir + fn, 'wb') as asset:
        chunk = fileitem.file.read(BUFFSIZE)
        while chunk:
            asset.write(chunk)
            chunk = fileitem.file.read(BUFFSIZE)


    # Create dictionary of values to pass
    MA['filename'] = fn
    MA['Account'] = form['Account'].value
    # Audit will go into a list to form a "table"
    AUDIT['User'] = form['User'].value
    AUDIT['IP_address'] = os.environ['REMOTE_ADDR']
    AUDIT['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S+0000",time.gmtime())
    AUDIT['Action'] = 'File uploaded'
    AUDIT['Notes'] = os.environ['HTTP_USER_AGENT']
    
    
    A = []
    A.append(AUDIT)
    
    MA['Group']=form['Group'].value
    MA['UserFields'] = USER
    MA['Audit'] = A
    # Turn Body in JSON message

    '''response = client.send_message(
    QueueUrl=url
    ,MessageBody='{"metadata": [%s]}' % str(MA).replace("'","\"")
    )'''
    
    
    INPUT = {
        'asset' : upload_dir + fn,
        'metadata' : MA,
    }

    workID = 'S-%s' %(str(uuid.uuid4()))
    
    response = sfn.start_execution(
      stateMachineArn='arn:aws:states:us-east-1:343744686176:stateMachine:IPD',
      name=workID,
      input=json.dumps(INPUT)
    )

    #print "Your file has been submitted to the state machine for processing. <br/> Please reference %s in the jobs page." %(workID)
    
    #print "<br/> %s" %(response)

    
    url = 'http://ec2-54-173-241-48.compute-1.amazonaws.com/upload.php'

    print 'Status: 302 Found'
    print 'Location:%s?id=%s' % (url,workID)
    print
    

else:
    print "there is issue"
