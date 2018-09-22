#!/bin/bash

cd site-packages
zip -r lambda.zip *
mv lambda.zip ../.
cd ..
zip -r -u  lambda.zip extractMetadataFromMediainfo.py lib/

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:835444431888:function:extractMetadataFromMediainfo --zip-file fileb://lambda.zip
