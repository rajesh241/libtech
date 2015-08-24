<?php
header('Content-type: text/plain');
$output = print_r($_GET, true);
#$callid=$_GET["CustomField"];
#file_put_contents("/tmp/myget.txt", $callid);
$myrand=rand(2,8);
$myaudio="http://libtech.avocadodesigns.in/exotel/audio/q1".$myrand.".wav";
#$myaudio="http://libtech.avocadodesigns.in/exotel/audio/1004_anupds.wav";
$myaudio="http://libtech.info/audio/1009_Bcastmah2905v2.wav";
$myaudio="http://libtech.info/audio/1121_523responsetomissedcall.wav";

echo $myaudio;
#echo '\n';
#echo $myaudio;

?>
