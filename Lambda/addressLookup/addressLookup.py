import logging
import googlemaps


logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """

    :param event:
    :param context:

    This function will perform two key tasks:
        1. Takes latitude and longitude input and passes to google
        
    """

    response = {}
    try:
        latitude = event['latitude']
        longitude = event['longitude']
        gKey = 'AIzaSyASc8ExetKga4u1ZDHBs4-VxUwjgbHzu1U' # This should be an environmental var
        
        logger.info("Performing lookup for lat {}\t lon {}".format(latitude, longitude))
        logger.info("Google maps client key: {}".format(gKey))
        gmaps = googlemaps.Client(key=gKey)
        
        address = gmaps.reverse_geocode((latitude, longitude))
        logger.info("Result set: {}".format(address))

        response['status'] = 0
        response['address'] = address[0]['formatted_address']

    
    except KeyError as e:
        response['status'] = 1
        response['message'] = "Input requires 'latitude' and 'longitude'. '{}' not found.".format(e)
    
    except Exception as e:
        response['status'] = 1
        response['message'] = "No address found: {}".format(e)
    
    return response
    