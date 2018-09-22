import boto3
import simplejson as json
import sys
import botocore
import subprocess
import shutil

sys.path.insert(0, '/Assets/sharedLibraries')
import databaseHelper
import parseHelper
import os
import fnmatch
import string
import math
import time




sfn = boto3.client('stepfunctions')

MA = {}
AUDIT = {}

def main(args):

    delTest(args)


def delTest(args):

    ARN = "arn:aws:states:us-east-1:343744686176:stateMachine:fileManager"
    
    if args[1] == 'v':
        #fileIn = testV
        sha1 = '6e508f0ed03da2b98ceb091827b569877037d1ef'
        fileKey = 'trim.6A7FE5FA-5321-4BF1-87D7-D26937142263_76ed9582-7da6-44ef-a0af-e22596297573'
        assetClass = 'Video'
    else:
        #fileIn = testI
        sha1 = 'afbf98c0070e5f048c21d7d17e24cd05401971f7'
        fileKey = 'image_509b2a45-de95-4757-9a4e-58d1e28b362a'
        assetClass = 'Image'

    sha1 = '0f8e2d57a1c7412a6d298a179ceaae643739e175'
    fileKey = 'IMG_3721_0893390a-37e2-4801-9a61-a7816944a43a'
    key = {
        'Checksum' : sha1,
    }

    INPUT = {
        'dbPrimaryKey' : key,
        'fileKey' : fileKey,
        'assetClass' : assetClass,
        'locationSource' : 'CDN',
        'locationDestination' : 'delete'
    }

    print json.dumps(INPUT)

    response = sfn.start_execution(
      stateMachineArn=ARN, # string
      name='test-%s' %(args[2]),
      input=json.dumps(INPUT)
    )

    print "Workflow requested: ", response


if __name__ == '__main__':
    
    main(sys.argv)