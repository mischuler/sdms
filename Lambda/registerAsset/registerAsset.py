import logging
import boto3
import botocore
import json
import decimal
import time

SIGNED_URL_EXPIRATION = 300     # The number of seconds that the Signed URL is valid


logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """

    :param event:
    :param context:

    This function registers the asset with the Asset Management database.
        1. Extract the document "DOC" from the incoming metadata
        2. Add additional information that is consistent across Exiftool and Mediainfo
        2. Attempt to register
    
    
    Future options:
        1. Dynamic database usage. Maybe use the Lamdba environment variables?
        2. Perform the registration immediately after we know the checksum,

        
    """
    
    logger.info("Begin registration of asset {} with checksum {}".format(event['key'],event['metadata']['checksum']))
    
    ############################################################
    # Add more information to the document
    DOC = event['DOC']
    DOC['Filename'] = event['filename']
    DOC['Extension'] = event['extension']
    DOC['Asset_Class'] = event['assetClass']
    DOC['Imported_Time'] = time.strftime("%Y-%m-%dT%H:%M:%S+0000",time.gmtime())
    DOC['File_Location'] = 'working'
    
    # Add a "GPS location" object. This is used for geo-searching with elasticsearch
    # Also use the location to reverse lookup an address
    # This will throw a KeyError if there is no GPS
    try:
    
        latitude = DOC['General']['Latitude']
        longitude = DOC['General']['Longitude']
    
        # This is setting the "location point"
        LOC = {'lat' : latitude, 'lon' : longitude}
        DOC['General']['location'] = LOC
        
        # This will call the function for address lookup
        addressQuery = {
            'latitude' : latitude
            , 'longitude' : longitude
        }
        lambdaClient = boto3.client('lambda')
        responseBody = lambdaClient.invoke(
            FunctionName = 'addressLookup'
            , Payload = json.dumps(addressQuery)
        )
        
        # Lambda invocations return a "botocore Streambody" in the Payload.
        # This must be READ then JSON Loaded to a dictionary
        # This will be the response data we want
        response = json.loads(responseBody["Payload"].read())
        
        if response['status'] == 0:
            DOC['General']['Address'] = response['address']
        
    except KeyError:
        pass
    
    # Add additional "Metadata" attributes found in the metadata
    for m in event['metadata']:
        DOC[m] = event['metadata'][m]
    
    # BOTO will throw an error loading "floating point" numbers into Dynamo
    # To fix this, the document must only contain type "Decimal" for our numerical items
    # The line below is a "hack" to convert the dictionary to JSON
    # and reload the JSON back into a dictionary, using the "parse_float" option
    DOC = json.loads(json.dumps(event['DOC']),parse_float=decimal.Decimal)
    registered = True


    #################################################################################
    # This is where we write the entry. Note that we use the CHECKSUM as a primary key
    # Registration WILL fail if the same file exists
    # There are two options if the registration fails
    #   1. Someone uploaded a previously deleted file. If this is the case, use a conditional update on:
    #       FILENAME 
    #       LOCATION
    #       USER
    #       Audit trail
    #   2. Else, fail
    # NOTE: Should we tie the index to account as well?
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('assets') # Maybe we parametrize the table in the future?
        
    try:
        table.put_item(
            Item = DOC,
            ConditionExpression = 'attribute_not_exists(checksum)'
        )
    
    # ConditionalCheckFailedException
    except botocore.exceptions.ClientError as err:
    
        # FUTURE: Grep for ConditionalCheckFailedException
        # We need to separate out actual client errors from put item errors
        logger.info("Entry already exists for: %s", DOC['checksum'])

        # Update the document. Set the PDL and thumbnail as NULL as well
        key = {
            'checksum' : DOC['checksum'],
            }
        
        updateExpression = 'SET File_Location = :d, Filename = :f, UserFields = :u, Audit = list_append(Audit, :a) REMOVE PDL, thumbnail, storyboard'
        conditionalExpression = 'File_Location = :l'
        
        expressionValues = {
            ':d' : 'working',
            ':a' : DOC['Audit'],
            ':u' : DOC['UserFields'],
            ':f' : DOC['Filename'],
            ':l' : 'delete'
        }
        
        logger.info("Attempting to update the item if it is deleted")
        try:
            result = table.update_item(
                Key = key,
                ConditionExpression = conditionalExpression,
                UpdateExpression = updateExpression,
                ExpressionAttributeValues = expressionValues,
                ReturnValues = 'UPDATED_OLD'
                )
            
            logger.info("Update result: %s", result )
        except botocore.exceptions.ClientError as err:
            logger.info("Update failed %s", str(err) )
            
            registered = False
            raise RegistrationFail('Registration failed: {}'.format(str(err)))
            

            
    event['registration'] = registered
    return event

class RegistrationFail(Exception): pass