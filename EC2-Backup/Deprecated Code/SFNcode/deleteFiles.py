""" This function accepts and asset, uploads it to S3, and adds a registration flag


author: Michael Schuler [mischuler@deloitte.com]

"""

import boto3
from botocore.client import Config
import botocore
import sys
import os
import string
import simplejson as json
import time

import logging
import logging.config

sys.path.insert(0, '/Assets/sharedLibraries')
import parseHelper
import databaseHelper

def main(args):

    taskName = os.path.basename(__file__)[:-3]
    ARN = "arn:aws:states:us-east-1:343744686176:activity:" + taskName

    logging.config.fileConfig('/Assets/sharedLibraries/logging_config.ini')
    logging.debug("Creating SFN boto client")
    botoConfig = Config(connect_timeout=50, read_timeout=70) # suggestion is the read is higher than connect
    sfn = boto3.client('stepfunctions', config=botoConfig)
    logging.debug("Created SFN boto client: %s", sfn)

    BUCKETNAME = "sdmscore"

    while True:

        task = sfn.get_activity_task(
            activityArn=ARN,
            workerName='%s-01' %(taskName)
        )

        if 'taskToken' not in task:
            logging.info("%s - Poll timed out, no new task. Repoll", taskName)
        
        # Run the operation
        else:
            taskToken = task['taskToken']
            workID = task['ResponseMetadata']['RequestId']
            logging.info("[%s] New request for %s", workID, taskName)

            INPUT = json.loads(task['input'])
            
            source = INPUT['locationSource']
            destination = INPUT['locationDestination']
            dbPrimaryKey = INPUT['dbPrimaryKey']
            fileKey = INPUT['fileKey'] + '/'
            
            # 
            if source in ['CDN', 'near_line']:

                logging.debug("[%s] Creating S3 bucket boto client", workID)
                s3 = boto3.resource('s3')
                bucket = s3.Bucket(BUCKETNAME)
                logging.debug("[%s] Created S3 bucket boto client", workID)
                
                for obj in bucket.objects.filter(Prefix=fileKey):
                    logging.debug("[%s] Deleting object: %s", workID, obj.key)
                    s3.Object(bucket.name, obj.key).delete()
            
            else: #Glacier
                continue # Add logic for glacier once supported
            
            AUDIT = {}
            AUDIT['User'] = 'System'
            AUDIT['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%S+0000",time.gmtime())
            AUDIT['Action'] = 'Asset removed from %s' % (source)
            AUDIT['Notes'] = workID
            
            # Add the Audit Dictionary to a list so that we can append it
            aLIST = []
            aLIST.append(AUDIT)
    
            updateExpression = 'set File_Location = :d, Audit = list_append(Audit, :a)'
            
            expressionValues = {
                ':d' : destination,
                ':a' : aLIST
            }
            # Call the update function
            logging.debug("[%s] Updating the asset location and history: %s", workID, destination)
            response = databaseHelper.updateEntry(dbPrimaryKey, updateExpression, expressionValues)       
            OUTPUT = {
                    'result' : 'success',
            }

            sfn.send_task_success(
                taskToken = taskToken,
                output = json.dumps(OUTPUT)
            )
                    
            logging.info("[%s] %s Complete", workID, taskName)

if __name__ == '__main__':
    
    main(sys.argv)
