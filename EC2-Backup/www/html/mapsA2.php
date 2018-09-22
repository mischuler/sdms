<?php 

require 'vendor/autoload.php';
use Aws\DynamoDb\DynamoDbClient;
use Aws\DynamoDb\Marshaler;

$sdk = new Aws\Sdk([
    'region'   => 'us-east-1',
    'version'  => 'latest',
	'credentials' => [
		'key' => 'AKIAIFPIHSMLJO2ODA6Q',
		'secret' => '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',
	],
]);


$dynamodb = $sdk->createDynamoDb();
$response = $dynamodb->scan([
    'TableName' => 'Assets'
]);

$marshaler = new Marshaler();

?>

<html>
<style>
      #map {
        width: 1200px;
        height: 900px;
      }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <script>

      var locations = [];

<?php

$item = "";

foreach ($response["Items"] as $object)
{
	$value = $marshaler->unmarshalItem($object);

        $time = ($value["General"]["recorded_date"] <> "") ? $value["General"]["recorded_date"] : $value["General"]["encoded_date"];
        $address = $value["General"]["Address"];
        //$time = $value["General"]["Recorded date"];
        $lat = $value["General"]["Latitude"];
        $long = $value["General"]["Longitude"];
        $fileName = $value["Filename"];
        $fileExt = $value["Extension"];
        $avail = $value["Distributed"];
        $thumb = $value["thumbnail"];
        $PDL = $value["PDL"];
        $description = $value["UserFields"]["Description"];
        $distributed = $value["Distributed"];
        $assetClass = $value["Asset Class"];
        #$item = '["'.$address.'|'.$time.'", "'.$lat.'", "'.$long.'"]';

	// Get URLs
	$baseURL = "https://s3.amazonaws.com/schulerfiles";
	
	$thumbURL = $baseURL.'/'.$fileName.$thumb;
	if (strcmp($assetClass, 'Image') == 0)
        $fileURL = $baseURL.'/'.$fileName.'/'.$fileName.$fileExt; // repeat filename twice to get into the appropriate folder
    else
        $fileURL = $baseURL.'/'.$fileName.$PDL;

    
	$content = '"<p><img src="'.$thumbURL.'"><br/> <a href="'.$fileURL.'">View</a><br/>'.$address.'|'.$time.'</p><p>'.$description.'</p>';
	
	#echo $content."<br/>";
	
	$item = "['".$content."', '".$lat."', '".$long."']";
	if (strcmp($distributed,'Y') == 0)
        echo 'locations.push('.$item.');
';
}

?>


	function initialize() {
        var mapDiv = document.getElementById('map');
        var map = new google.maps.Map(mapDiv, {
          center: {lat: 44.540, lng: -78.546},
          zoom: 4
        });
      

	var lat, lon, latlon;
	console.log(locations.length);

	for (i = 0; i < locations.length; i++)
	{
		
		addMarker(locations[i]);
		
		/*lat = locations[i][1];
		lon = locations[i][2];	
	
		latlon = new google.maps.LatLng(lat, lon);
		marker = new google.maps.Marker({
			position: latlon, map: map
			});

		console.log(lat);
		console.log(lon);
		infowindow = new google.maps.InfoWindow({ 
			content: locations[i][0]
			});
		
		marker.addListener('click', function() {
				infowindow.open(map, marker);
			});

		marker.setMap(map);*/		
	}
	
	function addMarker( location ) {
		
	
		var marker = new google.maps.Marker({
			position: new google.maps.LatLng( location[1], location[2] ), map: map
	});
	
		var infowindow = new google.maps.InfoWindow({
                        content: location[0]
		});

                marker.addListener('click', function() {
                                infowindow.open(map, marker);
                });

		marker.setMap(map);
	}
}	

    </script>
    <script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyASc8ExetKga4u1ZDHBs4-VxUwjgbHzu1U&callback=initialize"
        async defer></script>
  </body>
</html>
