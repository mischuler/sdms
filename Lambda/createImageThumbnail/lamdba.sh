#!/bin/bash

zip lambda.zip createImageThumbnail.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:835444431888:function:createImageThumbnail --zip-file fileb://lambda.zip
