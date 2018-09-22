#!/bin/bash

zip lambda.zip scanForVirus.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:835444431888:function:scanForVirus --zip-file fileb://lambda.zip
