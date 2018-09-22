<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Schuler Digital Media Services</title>

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
            <li><a href="portal.html">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="jobs.php">Jobs</a></li>
            <li><a href="upload.php">Upload file</a></li>
            <li class="active"><a href="files.php">View files</a></li>
            <li><a href="maps.php">View map</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </nav>

<?php
include("search.php");
?>
    <div class="table-responsive">
    <table class="table table-striped">
    <thead class="thead-default">
        <tr>
        <th>Thumbnail</th>
        <!-- <th>File</th> -->
        <th>Extension</th>
        <th>Asset Class</th>
        <th>SHA1 Checksum</th>
        <th>Description</th>
        <th>Address</th>
        <th>Date recorded</th>
        <th>Device make</th>
        <th>Devide model</th>
        <th>Upload history</th>
        </tr>
    </thead>
    <tbody>
<?php

$item = "";
$id = 0;
$modals = array();

foreach ($response['hits']['hits'] as $doc)
{
    $value = $doc['_source'];
    
    $PDL = $value["PDL"];
    $lat = $value["General"]["Latitude"];
    $long = $value["General"]["Longitude"];

    $time = ($value["General"]["recorded_date"] <> "") ? $value["General"]["recorded_date"] : $value["General"]["encoded_date"];
    $address = $value["General"]["Address"];
    $thumb = $value["thumbnail"];
    $fileName = $value["Filename"];
    $fileExt = $value["Extension"];
    $assetClass = $value["Asset_Class"];
    $audit = $value["Audit"][0];
    $sha1 = $value["Checksum"];
    $description = $value["UserFields"]["Description"];
    $make = $value["General"]["make"];
    $model = $value["General"]["model"];
    #$item = '["'.$address.'|'.$time.'", "'.$lat.'", "'.$long.'"]';

    // Get URLs
    $baseURL = "https://s3.amazonaws.com/schulerfiles";
    $baseURL = "https://d2emf5g0sf66fv.cloudfront.net";

    $thumbURL = $baseURL.'/'.$fileName.$thumb;
    if (strcmp($assetClass, 'Image') == 0) {
        $fileURL = $baseURL.'/'.$fileName.'/'.$fileName.$fileExt; // repeat filename twice to get into the appropriate folder
        $player = '<img src="'.$fileURL.'" width="1000">';
    } else {
        $fileURL = $baseURL.'/'.$fileName.$PDL;
        $player = '<video width="640" height="360" controls><source src="'.$fileURL.'" type="video/mp4">';
    }
    
    
    // Add the modal content to a separate php array. Echo it at the bottom
    $modalContent = '<div class="modal fade" id="myModal'.$id.'" tabindex="-1" role="dialog" aria-labelledby="myModalLabel'.$id.'">' .
                        '<div class="modal-dialog" role="document">'.
                            '<div class="modal-content">' .
                                '<div class="modal-header">' .
                                    '<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>'.
                                    '<h4 class="modal-title" id="myModalLabel'.$id.'">'.$fileName.'</h4>'.
                                '</td>'.
                                '<div class="modal-body">'.$player.'</td>'.
                                 '</td></td></td>'.
                                '';
    $modalContent = $modalContent . '</div></div></div></div></div>';
    
    
    $auditLog = "";

        foreach($audit as $a) {
            $auditLog = $auditLog.$a.'<br/>';
        }

        $modalButton = '<a href="#" data-toggle="modal" data-target="#myModal'.$id.'">';    
        $thumbLink = '<img src="'.$thumbURL.'" class="img-thumbnail">';
        echo '<tr>';
        echo '<td>'.$modalButton.$thumbLink.'</a></td>';
        #echo '<td>'.$fileName.'</td>';
        echo '<td>'.$fileExt.'</td>';
        echo '<td>'.$assetClass.'</td>';
        echo '<td>'.$sha1.'</td>';
        echo '<td>'.$description.'</td>';
        echo '<td>'.$address.'</td>';
        echo '<td>'.$time.'</td>';
        echo '<td>'.$make.'</td>';
        echo '<td>'.$model.'</td>';
        echo '<td>'.$auditLog.'</td>';
        echo '</tr>';
        
        array_push($modals, $modalContent);


    $id = $id + 1;
}

?>
</tbody>
</table>
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
    <script>window.jQuery || document.write('<script src="/js/vendor/jquery.min.js"><\/script>')</script>
    <script src="/js/bootstrap.min.js"></script>
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <script src="/js/ie10-viewport-bug-workaround.js"></script>
  </body>
</html>