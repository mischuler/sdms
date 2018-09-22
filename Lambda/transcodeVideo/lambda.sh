#!/bin/bash

zip lambda.zip transcodeVideo.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:835444431888:function:transcodeVideo --zip-file fileb://lambda.zip
