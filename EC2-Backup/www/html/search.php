
<link rel="stylesheet" href="/js/jquery-ui.css">
<div class="container">

      <div class="starter-template">
        <p class="lead">Enter your search parameters</p>
<?php
echo '<form method="post" action="'.str_replace("/","",$_SERVER["REQUEST_URI"]).'" enctype="multipart/form-data">';
?>

<input name="Account" type="hidden" value="Account1" />
            Free text search
            <input name="free" type="text" size=50 placeholder="Enter key words to search on"/> <br/>
        
        
            Location / radius 
            <input type="text" name="locale" size=50 id="autocomplete" placeholder="Enter search address" onfocus="geolocate()" /> 
            <input name="radius" placeholder="Radius in miles" type="text" /> <br/>
        
            Date range 
            <input id="startpick" type="text" name="dateStart" placeholder="Start date" /> 
            <input id="endpick" name="dateEnd" type="text" placeholder="End date"/> <br/>
        
        
        <input type="submit" value="Search" />
        </form>
     </div>
      

    </div><!-- /.container -->
<hr/>
 <script>
      // This example displays an address form, using the autocomplete feature
      // of the Google Places API to help users fill in the information.

      // This example requires the Places library. Include the libraries=places
      // parameter when you first load the API. For example:
      // <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

      var placeSearch, autocomplete;

      function initAutocomplete() {
        // Create the autocomplete object, restricting the search to geographical
        // location types.
        autocomplete = new google.maps.places.Autocomplete(
            /** @type {!HTMLInputElement} */(document.getElementById('autocomplete')),
            {types: ['geocode']});

        
      }

      // Bias the autocomplete object to the user's geographical location,
      // as supplied by the browser's 'navigator.geolocation' object.
      function geolocate() {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(function(position) {
            var geolocation = {
              lat: position.coords.latitude,
              lng: position.coords.longitude
            };
            var circle = new google.maps.Circle({
              center: geolocation,
              radius: position.coords.accuracy
            });
            autocomplete.setBounds(circle.getBounds());
          });
        }
      }
    </script>

<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyASc8ExetKga4u1ZDHBs4-VxUwjgbHzu1U&libraries=places&callback=initAutocomplete"
        async defer></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
<script src="/js/jquery-ui.js"></script>
<script>
  $( function() {
    $( "#startpick" ).datepicker({
        showButtonPanel: true,
        changeMonth: true,
        changeYear: true
    });
    $( "#endpick" ).datepicker({
        showButtonPanel: true,
        changeMonth: true,
        changeYear: true
    });
  } );
  


</script>
<?php

require 'vendor/autoload.php';
use Elasticsearch\ClientBuilder;

$esEndpoint = 'https://search-hank-2rnvrx32jfys5zigk7ntltqqsq.us-east-1.es.amazonaws.com:443';
$esIndex = 'assets';
$esType = 'assets_type';
#$dynamodb = $sdk->createDynamoDb();

$hosts = [ $esEndpoint ];

//$client = ClientBuilder::create()           // Instantiate a new ClientBuilder
//                   ->setHosts($hosts)      // Set the hosts
//                    ->build();              // Build the client object

$clientB = ClientBuilder::create();
$clientB->setHosts($hosts);
$client = $clientB->build();

$searchD = false;
$searchL = false;

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $free = trim($_POST['free']);
    $lat = trim($_POST['lat']);
    $lon = trim($_POST['lon']);
    $dateStart = trim($_POST['dateStart']);
    $dateEnd = trim($_POST['dateEnd']);
    $address = trim($_POST['locale']);
    $radius = trim($_POST['radius']);
    
}

// If we select an address
// 1. try to look the address up via google
// 2. If successful, get the lat, lon, and set the location search flag to true
// 3. Set a default radius of 5 miles if nothing is given
if (!empty($address)) {
    $data_arr = pgeocode($address); 
    // if able to geocode the address
    if($data_arr){

        $searchL = true;
        $latitude = $data_arr[0];
        $longitude = $data_arr[1];
    }
    
    if (empty($radius)) {
        $radius = 5;
    }
}

// Set a flag that we will search by date
if (!empty($dateStart) or !empty($dateEnd)) {
    $searchD = true;
}

// Sets boundaries for start and end dates if not given.
if (empty($dateStart)) {
    $dateStart = '01/01/1971';
}

if (empty($dateEnd)) {
    $dateEnd = '12/12/2999';
}

// if the freetext is empty, set the search term for "anything"
// otherwise, search across the term
if (empty($free)) {
    #$searchTerm = ['match_all' => [] ];
    $searchTerm = ['match_all' => [ "boost" => 1.0,] ]; # boost is a work-around for error that occurs in ES5.0
}
else {
    $searchTerm = ['match' => ['_all' => $free] ];
}

if ($searchL) {

    $params = [
        'index' => $esIndex,
        'type' => $esType,
        'body' => [
            'from' => 0,
            'size' => 100,
            'sort' => [
                'Imported_Time' => [
                    'order' => "desc"
                ]
            ],
          'query' => [
                'bool' => [
                    'must' => [
                        $searchTerm,
                    ],
                    'filter' => [
                        'bool' => [
                            'must' => [
                                ['match' => [ 'File_Location' => 'CDN'] ],
                                ['geo_distance' => [ 'distance' => $radius, 'unit' => 'mi', 'General.location' => [ 'lat' => $latitude, 'lon' => $longitude ] ] ],
                                ['range' => [ 'General.recorded_date' => [ 'gte' => $dateStart, 'lte' => $dateEnd, 'format' => 'MM/dd/yyyy' ] ] ]
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ];
        
}
elseif ($searchD) {
    $params = [
        'index' => $esIndex,
        'type' => $esType,
        'body' => [
            'from' => 0,
            'size' => 100,
            'sort' => [
                'Imported_Time' => [
                    'order' => "desc"
                ]
            ],
          'query' => [
                'bool' => [
                    'must' => [
                        $searchTerm,
                    ],
                    'filter' => [
                        'bool' => [
                            'must' => [
                                ['match' => [ 'File_Location' => 'CDN'] ],
                                ['range' => [ 'General.recorded_date' => [ 'gte' => $dateStart, 'lte' => $dateEnd, 'format' => 'MM/dd/yyyy' ] ] ]
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ];
        
}
else {
    $params = [
        'index' => $esIndex,
        'type' => $esType,
        'body' => [
            'from' => 0,
            'size' => 100,
            'sort' => [
                'Imported_Time' => [
                    'order' => "desc"
                ]
            ],
          'query' => [
                'bool' => [
                    'must' => [
                        $searchTerm,
                    ],
                    'filter' => [
                        'bool' => [
                            'must' => [
                                ['match' => [ 'File_Location' => 'CDN'] ]
                            ]
                        ]
                    ]
                ]
            ]
        ]
    ];
}

$response = $client->search($params);
$milliseconds = $response['took'];
$results = $response['hits']['total'];

echo $results.' documents returned in '.$milliseconds.' milliseconds';
echo '<hr/>';


// function to geocode address, it will return false if unable to geocode address
function pgeocode($address){
 
    // url encode the address
    $address = urlencode($address);
     
     
    // google map geocode api url
    $url = "http://maps.google.com/maps/api/geocode/json?address={$address}";
 
    // get the json response
    $resp_json = file_get_contents($url);
     
    // decode the json
    $resp = json_decode($resp_json, true);
 
    // response status will be 'OK', if able to geocode given address 
    if($resp['status']=='OK'){
 
        // get the important data
        $lati = $resp['results'][0]['geometry']['location']['lat'];
        $longi = $resp['results'][0]['geometry']['location']['lng'];
        $formatted_address = $resp['results'][0]['formatted_address'];
         
        // verify if data is complete
        if($lati && $longi && $formatted_address){
         
            // put the data in the array
            $data_arr = array();            
             
            array_push(
                $data_arr, 
                    $lati, 
                    $longi, 
                    $formatted_address
                );
             
            return $data_arr;
             
        }else{
            return false;
        }
         
    }else{
        return false;
    }
}


?>
