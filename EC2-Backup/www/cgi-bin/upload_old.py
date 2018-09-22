#!/usr/bin/python
print "Content-type: text/html"
print
print "<pre>"
import os, sys
import boto3
import string
import cgi
import cgitb
import subprocess
import time
import uuid

sys.path.insert(0, '/home/ec2-user/code')
import logger


# ENABLES DEBUG ON WEBPAGE
cgitb.enable()

# Sets up SQS client and gets the URL of our Queue
client = boto3.client('sqs')
response = client.get_queue_url(QueueName='Asset')
url = response['QueueUrl']

# Puts all the fields from the webpage
form = cgi.FieldStorage()

# Process input
try:
    fileitem = form['asset']
except KeyError:
    print "Upload a file OR ELSE"
    exit()


USER = {}
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

    #open(upload_dir + fn, 'wb').write(fileitem.file.read())
    with open(upload_dir + fn, 'wb') as asset:
        chunk = fileitem.file.read(BUFFSIZE)
        while chunk:
            asset.write(chunk)
            chunk = fileitem.file.read(BUFFSIZE)


    # Create dictionary of values to pass
    MA['filename']=fn
    MA['path']=upload_dir
    MA['UploadTime']=time.strftime("%Y-%m-%dT%H:%M:%S+0000",time.gmtime())
    MA['SourceIP']=os.environ['REMOTE_ADDR']
    MA['UserAgent']=os.environ['HTTP_USER_AGENT']
    MA['Account']=form['Account'].value
    MA['Group']=form['Group'].value
    MA['User']=form['User'].value
    MA['UserFields'] = USER
    # Turn Body in JSON message

    response = client.send_message(
    QueueUrl=url
    ,MessageBody='{"metadata": [%s]}' % str(MA).replace("'","\"")
    )

    print "Your file has been upload and notification has been sent to the queue"

else:
    print "there is issue"



print "hello"
