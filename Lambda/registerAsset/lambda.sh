#!/bin/bash

zip lambda.zip registerAsset.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:835444431888:function:registerAsset --zip-file fileb://lambda.zip
