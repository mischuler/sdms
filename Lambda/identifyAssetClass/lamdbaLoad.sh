#!/bin/bash

zip iden.zip identifyAssetClass.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:343744686176:function:identifyAssetClass --zip-file fileb://iden.zip
