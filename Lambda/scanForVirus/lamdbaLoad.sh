#!/bin/bash

zip scan.zip scanForVirus.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:343744686176:function:scanForVirus --zip-file fileb://scan.zip
