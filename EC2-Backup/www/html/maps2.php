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

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Schuler's crazy experiment</title>

    <!-- Bootstrap core CSS -->
    <link href="/css/bootstrap.min.css" rel="stylesheet">

    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <link href="/css/ie10-viewport-bug-workaround.css" rel="stylesheet">

    <!-- Custom styles for this template -->
    <link href="/css/starter-template.css" rel="stylesheet">

    <!-- Just for debugging purposes. Don't actually copy these 2 lines! -->
    <!--[if lt IE 9]><script src="../../assets/js/ie8-responsive-file-warning.js"></script><![endif]-->
    <script src="/js/ie-emulation-modes-warning.js"></script>

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.3/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
    
  <style>
  #map { width: 1200px;
        height: 900px;
      }
</style>
  </head>

  <body>

    <nav class="navbar navbar-inverse navbar-fixed-top">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="#">Bridging digitally</a>
        </div>
        <div id="navbar" class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li><a href="#">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
            <li><a href="upload.html">Upload file</a></li>
            <li><a href="upload.html">View files</a></li>
            <li class="active"><a href="maps.php">View map</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </nav>

    
    <div class="container">

    <div id="map"></div>
    <script>

    var locations = [];

<?php

$item = "";
$id = 0;
$modals = array();

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
    $baseURL = "https://dnt4vq51jg2tj.cloudfront.net";

    $thumbURL = $baseURL.'/'.$fileName.$thumb;
    if (strcmp($assetClass, 'Image') == 0) {
        $fileURL = $baseURL.'/'.$fileName.'/'.$fileName.$fileExt; // repeat filename twice to get into the appropriate folder
        $player = '<img src="'.$fileURL.'" width="1000">';
    } else {
        $fileURL = $baseURL.'/'.$fileName.$PDL;
        $player = '<video width="640" height="360" controls><source src="'.$fileURL.'" type="video/mp4">';
    }
    // This gets complicated because we need to create a dynamic modal. This is probably horribly inefficient but that's ok
    // Assign each button a uniqueModal using the checksum
    $modalButton = '<button type="button" class="btn btn-primary btn-lg" data-toggle="modal" data-target="#myModal'.$id.'"> View file </button>';
    
    // Add the modal content to a separate php array. Echo it at the bottom
    $modalContent = '<div class="modal fade" id="myModal'.$id.'" tabindex="-1" role="dialog" aria-labelledby="myModalLabel'.$id.'">' .
                        '<div class="modal-dialog" role="document">'.
                            '<div class="modal-content">' .
                                '<div class="modal-header">' .
                                    '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'.
                                    '<h4 class="modal-title" id="myModalLabel'.$id.'">'.$fileName.'</h4>'.
                                '</div>'.
                                '<div class="modal-body">'.$player.'</div>'.
                                 '</div></div></div>'.
                                '';
    
    array_push($modals, $modalContent);
    
    //$content = '"<p><img src="'.$thumbURL.'"><br/> <a href="'.$fileURL.'">View</a><br/>'.$address.'|'.$time.'</p><p>'.$description.'</p>';
    $content = '"<p><img src="'.$thumbURL.'"><br/>'.$address.'|'.$time.'</p><p>'.$description.'</p><br/>'.$modalButton.'"';

    $item = "['".$content."', '".$lat."', '".$long."']";
    
    $id = $id + 1;
    // Only add a "Distributed" asset
    
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


    </div><!-- /.container -->
<?php

// At modal to HTML
foreach ($modals as $mHtml)
{
    echo $mHtml;
    
}?>



    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="/js/vendor/jquery.min.js"><\/script>')</script>
    <script src="/js/bootstrap.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="/js/ie10-viewport-bug-workaround.js"></script>
  </body>
</html>