#!/bin/bash

zip lambda.zip assetsToElastic.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:835444431888:function:assetsToElastic --zip-file fileb://lambda.zip
