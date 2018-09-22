import logging
import googlemaps


logger = logging.getLogger('boto3')
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """

    :param event:
    :param context:

    this function:
        1. Accepts an address
        2. Uses the address to look up coordinates via googlemaps
        3. Returns a latLon dictionary {lat: $lat, lon: $lon}
        
    """

    response = {}
    try:
        address = event['address']
        gKey = 'AIzaSyASc8ExetKga4u1ZDHBs4-VxUwjgbHzu1U' # This should be an environmental var
        
        logger.info("Performing lookup for address {}".format(address))
        logger.info("Google maps client key: {}".format(gKey))
        gmaps = googlemaps.Client(key=gKey)
        
        address = gmaps.geocode(address)
        logger.info("Result set: {}".format(address))

        response['status'] = 0
        response['latLon'] = {}
        response['latLon']['lat'] = address[0]['geometry']['location']['lat']
        response['latLon']['lon'] = address[0]['geometry']['location']['lng']
    
    except KeyError as e:
        response['status'] = 1
        response['message'] = "Input requires an 'address'".format(e)
    
    except Exception as e:
        response['status'] = 1
        response['message'] = "Address lookup failed: {}".format(e)
    
    logger.info("Response is: {}".format(response))
    
    return response
    