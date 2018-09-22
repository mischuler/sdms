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

        $time = ($value["General"]["Recorded date"] <> "") ? $value["General"]["Recorded date"] : $value["General"]["Encoded date"];
        $address = $value["General"]["Address"];
        //$time = $value["General"]["Recorded date"];
        $lat = $value["General"]["Latitude"];
        $long = $value["General"]["Longitude"];
	$filename = $value["Filename"];
        #$item = '["'.$address.'|'.$time.'", "'.$lat.'", "'.$long.'"]';

	// Get URLs
	$noEXT = pathinfo($filename, PATHINFO_FILENAME);
	$keyframeurl = "https://s3.amazonaws.com/schulerfiles/";
	
	$thumb = $keyframeurl.$noEXT."/".$noEXT."_thumbnail.jpg";
	$file = $keyframeurl.$noEXT."/".$noEXT.".mp4";

	$content = '"<p><img src="'.$thumb.'"><br/> <a href="'.$file.'">View</a><br/>'.$address.'|'.$time.'</p>"';
	
	#echo $content."<br/>";
	
	$item = "['".$content."', '".$lat."', '".$long."']";
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
