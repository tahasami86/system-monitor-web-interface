<?php
$influx_host = 'localhost';
$influx_port = '8086';
$db_name = 'system_monitoring';
$query = $_GET['q'];  // Get the query from the URL

// Create the InfluxDB query URL
$influx_url = "http://$influx_host:$influx_port/query?db=$db_name&q=" . urlencode($query);

// Send the query and get the response
$response = file_get_contents($influx_url);

// Output the response as JSON
header('Content-Type: application/json');
echo $response;
?>
