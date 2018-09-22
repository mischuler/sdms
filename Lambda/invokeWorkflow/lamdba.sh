#!/bin/bash

zip lambda.zip invokeWorkflow.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:835444431888:function:invokeWorkflow --zip-file fileb://lambda.zip
