#!/bin/sh

SCRIPTS=()

SCRIPTS+=('identifyAssetClass.py')
SCRIPTS+=('registerAsset.py')
SCRIPTS+=('extractExifMetadata.py')
SCRIPTS+=('extractMediaInfoMetadata.py')
SCRIPTS+=('createThumbnailFromImage.py')
SCRIPTS+=('createThumbnailFromVideo.py')
SCRIPTS+=('transcodeVideo.py')
SCRIPTS+=('distributeToS3.py')
SCRIPTS+=('cleanUpLandingPad.py')
SCRIPTS+=('moveFiles.py')
SCRIPTS+=('deleteFiles.py')


for i in "${SCRIPTS[@]}"
do
	if [ "$1" == "start" ]; then 
		python $i &
	else
		id=`ps u | grep "[p]ython ${i}"`
		idA=($id)
		`kill ${idA[1]}`
	fi
done



