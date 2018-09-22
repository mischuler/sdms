# -*- coding: utf-8 -*-

import boto3
import botocore

# This is where we write the entry. Note that we use the CHECKSUM as a primary keyu
# Registration WILL fail if the same file exists
# NOTE: Should we tie the index to account as well?
def writeEntry(DOC):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Assets')
        
    try:
        table.put_item(
            Item = DOC,
            ConditionExpression = 'attribute_not_exists(Checksum)'
        )
    except botocore.exceptions.ClientError as err:
        result = { 
            'reason' : 'REG-0001_Duplicate file entry: The file with ID %s already exists' %(DOC['Checksum']),
            'detail' : str(err)
        }
    else:
        result = { 
            'Checksum' : DOC['Checksum'] 
        }

    return result

# Database updates expect:
# Primary Key [Dictionary] of the file
# The update expression
# The update values
# Return Values [Optional]
# Note: We should add in a parameter to fail if the primary key is not found
def updateEntry(key, updateExpression, expressionValue, returnValues='NONE'):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Assets')
    #print key, updateExpression, expressionValue, returnValues
    response = table.update_item(
        Key = key,
        UpdateExpression = updateExpression,
        ExpressionAttributeValues = expressionValue,
        ReturnValues = returnValues
        )
    
    return response
    
    
def deleteEntry(key):
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Assets')
    
    response = table.delete_item(
        Key = key,
        )
    
    return response
        