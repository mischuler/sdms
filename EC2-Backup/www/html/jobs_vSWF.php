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
            <li class="active"><a href="jobs.php">Jobs</a></li>
            <li><a href="upload.html">Upload file</a></li>
            <li><a href="files.php">View files</a></li>
            <li><a href="maps.php">View map</a></li>
          </ul>
        </div><!--/.nav-collapse -->
      </div>
    </nav>
    
    
     <div class="starter-template">
        <h1>View open and closed jobs</h1>
        <p class="lead">This will display the last 25 open or closed jobs from the last week</p>
      </div>

    <div class="table-responsive">
    <table class="table table-striped">
    <thead class="thead-default">
        <th>Workflow ID</th>
        <!-- <th>File</th> -->
        <th>Status</th>
        <th>Start Timestamp</th>
        <th>End Timestamp</th>
        <th>Execution (seconds)</th>
    </tr>
    </thead>
    <tbody>

<?php
require 'vendor/autoload.php';
use Aws\Swf\SwfClient;

$client =  SwfClient::factory([
    'region'   => 'us-east-1',
    'version'  => 'latest',
	'credentials' => [
		'key' => 'AKIAIFPIHSMLJO2ODA6Q',
		'secret' => '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',
	],
]);
date_default_timezone_set('America/New_York');

$objDateTime = new DateTime('NOW');
$objDateTime -> sub(new DateInterval('P1D'));

$nixTime = time() - (60*60 * 24 * 7);

$resultO = $client->listOpenWorkflowExecutions([
    'domain' => 'ITD', // REQUIRED
    'startTimeFilter' => [ // REQUIRED
        'oldestDate' => $nixTime, // REQUIRED
    ],
    'maximumPageSize' => 25,
    'typeFilter' => [
        'name' => 'defaultRun', // REQUIRED
        'version' => '2',
    ],
]);

$resultC = $client->listClosedWorkflowExecutions([
    'domain' => 'ITD', // REQUIRED
    'maximumPageSize' => 25,
        'startTimeFilter' => [ // REQUIRED
        'oldestDate' => $nixTime, // REQUIRED
    ],
    'typeFilter' => [
        'name' => 'defaultRun', // REQUIRED
        'version' => '2',
    ],
]);

foreach ($resultO['executionInfos'] as $doc)
{
    $workId = $doc['execution']['workflowId'];
    $status = $doc['executionStatus'];
    $start = $doc['startTimestamp'];
    $end = $doc['closeTimestamp'];
    
        echo '<tr>';
        echo '<td>'.$workId.'</td>';
        #echo '<div class="col-md-1">'.$fileName.'</div>';
        echo '<td>'.$status.'</td>';
        echo '<td>'.$start.'</td>';
        echo '<td>'.$end.'</td';
        echo '</tr>';
        
}


foreach ($resultC['executionInfos'] as $doc)
{
    $workId = $doc['execution']['workflowId'];
    $status = $doc['executionStatus'];
    $start = $doc['startTimestamp'];
    $end = $doc['closeTimestamp'];
    
    $diff = abs(strtotime($start) - strtotime($end));
    
        echo '<tr>';
        echo '<td>'.$workId.'</td>';
        #echo '<div class="col-md-1">'.$fileName.'</div>';
        echo '<td>'.$status.'</td>';
        echo '<td>'.$start.'</td>';
        echo '<td>'.$end.'</td>';
        echo '<td>'.$diff.'</td>';
        echo '</tr>';
        
}
?>
</tbody>
</table>
</div>
    
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