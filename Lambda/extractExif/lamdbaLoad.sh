#!/bin/bash

cd ExifToolFiles
zip -r exif.zip *
mv exif.zip ../.
cd ..
zip -u exif.zip extractMetadataFromExiftool.py

aws lambda update-function-code --function-name arn:aws:lambda:us-east-1:343744686176:function:extractMetadataFromExiftool --zip-file fileb://exif.zip
