#!/bin/bash

cd site-packages
zip -r lambda.zip *
mv lambda.zip ../.
cd ..
zip -u  lambda.zip searchAssets.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:835444431888:function:searchAssets --zip-file fileb://lambda.zip
