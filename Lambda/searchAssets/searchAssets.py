import logging
import boto3
import json
from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch_dsl import Search, connections
#import certifi
from requests_aws4auth import AWS4Auth



logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """

    :param event:
    :param context:
    """ 
    
    # get session information and use this information
    # to create a "signed" AWS object
    session = boto3.session.Session()
    credentials = session.get_credentials()
    
    awsauth = AWS4Auth(
        credentials.access_key, 
        credentials.secret_key, 
        session.region_name, 
        'es',
        session_token=credentials.token
    )
    
    ##############################
    # Get parametrized objects
    esHost = "https://search-hank-6twba3vhs6beld5vm2d3wixuru.us-east-1.es.amazonaws.com" # Parametrize this
    esIndex = "assets"

    
    
    #####################################
    # Get all the keys. Expected options are:
    # 1. Account ID -- Are these assets in my account?
    # 2. Case ID -- Search within a specific case
    # 3. Free Text -- Search over the asset metadata for words
    # 4. Address -- Address used to pull lat / lon
    # 5. Search Radius -- Expected radius to search around the lat/lon
    # 6. Start Date -- The lower bound of when a file was recorded
    # 7. End Date -- The upper bound of when a file was recorded

    logger.info("Event data: {}".format(event))
    
    searchLocation = False
    searchDate = False
    searchText = False
    
    # Each key will be wrapped in a try catch
    # Account
    try:
        accountId = event['accountId']
    except KeyError:
        accountId = 'account1'
        logger.info("Setting default account")
        
    # Group
    try:
        groupId = event['groupId']
    except KeyError:
        groupId = 'group1'
        logger.info("Setting default group")
    
    # Case ID
    try:
        caseId = event['caseId']
    except KeyError:
        caseId = '*'
        logger.info("Setting default case ID")
    
    # Free Text
    try:
        freeText = event['freeText'].strip()
    except KeyError:
        freeText = ''
        logger.info("Setting default freetext group")
    # This makes sure there is actual text to search for
    if freeText != '':
        searchText = True
        logger.info("Setting searchText to true")
    
    # Address
    try:
        address = event['address']
        # perform address look up
        
        addressQuery = {
            'address' : address
        }
        
        logger.info("Fetching address information for: {}".format(address))
        lambdaClient = boto3.client('lambda')
        responseBody = lambdaClient.invoke(
            FunctionName = 'latLonLookup'
            , Payload = json.dumps(addressQuery)
        )
        logger.info("Response information: {}".format(responseBody))
        # Lambda invocations return a "botocore Streambody" in the Payload.
        # This must be READ then JSON Loaded to a dictionary
        # This will be the response data we want
        
        response = json.loads(responseBody["Payload"].read())
        
       
        if response['status'] == 0:
            latLon = response['latLon']
            searchLocation = True
            logger.info("Setting location search to True")
        else:
            logger.info("Exception during address lookup: {}".format(response))
    except KeyError:
        searchLocation = False
        logger.info("Setting location search to false")        
    
    # Radius
    try:
        radius = event['radius']
    except KeyError:
        radius = 5
        logger.info("Setting default search radius")    
    
    # Dates
    # If we don't have any dates, search dates is false
    # ...
    try:
        startDate = event['startDate']
        searchDate = True
    except KeyError:
        startDate = '01/01/1971'
        logger.info("Setting default start date")

    try:
        endDate = event['endDate']
        searchDate = True
    except KeyError:
        endDate = '12/31/9999'
        logger.info("Setting default end date")    
            
    
    
    ########################################
    # Start the connection to ElasticSearch
    # We need to use the ElasticSearch RequestsHttpConnection, with the AWS auth object
    logger.info("Connecting to the esHost '{}'...".format(esHost))
    connections.create_connection(hosts=[esHost], 
        http_auth=awsauth, 
        #ca_certs=certifi.where(),
        verify_certs=True,
        use_ssl=True,
        connection_class=RequestsHttpConnection
    )
    logger.info("Connection successful")
    
    ######################################
    # Start to chain the query together
    # 1. Set the account and sort
    # 2. Add the "text" search if available
    # 3. Add the date parameters if available
    # 4. Add the location parameters if available
    #
    # Additionally, we only want to return certain fields to limit the return information
    #   Checksum
    #   Address
    #   Date Imported
    #   Description
    #   Case ID
    #   Lat / Lon
    #   Thumbnail
    #   Extension
    #   Asset Class
    #   Device Make and Model
    #   Audit History
    #   NOTE: TO-DO THIS LATER
    
    assetSearch = Search(index=esIndex) \
        .sort('-Imported_Time') \
        .filter("match",account=accountId)
    
    if searchText:
        assetSearch = assetSearch.query("query_string",query=freeText)
    if searchDate:
        dateFormat = 'MM/dd/yyyy'
        assetSearch = assetSearch.filter('range',General__recorded_date={'gte': startDate, 'lt': endDate, 'format': dateFormat})
    if searchLocation:
        assetSearch = assetSearch.filter('geo_distance',distance=radius,unit='mi',General__location=latLon)
        # Location should be a dictionary of "Lat and lon"
    
    logger.info("Executing the following search query: {}".format(assetSearch.to_dict()))
    response = assetSearch.execute()
    logger.info("{} documents returned in {} milliseconds".format(response.hits.total, response.took))
    #logger.info(response.to_dict())    
    return response.to_dict()
        
class searchAssetsFail(Exception): pass