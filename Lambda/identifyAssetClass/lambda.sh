#!/bin/bash

zip lamdba.zip identifyAssetClass.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:835444431888:function:identifyAssetClass --zip-file fileb://lambda.zip
