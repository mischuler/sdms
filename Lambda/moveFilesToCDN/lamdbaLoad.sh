#!/bin/bash

zip lambda.zip moveFilesToCDN.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:343744686176:function:moveFilesToCDN --zip-file fileb://lambda.zip
