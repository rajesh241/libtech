<?php
header('Content-type: text/plain');
include ("./params.php");
$mydbcon = mysqli_connect($dbserver,$dbuser,$dbpasswd);
$sid=$_GET["CallSid"];
$digits=$_GET["digits"];
$digits=str_replace('"','',$digits);
file_put_contents("/tmp/myfeedback.txt", $sid.$digits);

$query="use libtech";
mysqli_query($mydbcon,$query);
$query="insert into callFeedback (sid,feedback) values ('".$sid."','".$digits."');";
mysqli_query($mydbcon,$query);
#$query="select audio from callQueue where id=".$sid;
#$query="select audio from callQueue where id=5";
#$result=mysqli_query($mydbcon,$query);
#$row=mysqli_fetch_array($result);
#$audio=$row['audio'];
#$audioarray=explode(",",$audio);
#file_put_contents("/tmp/myget.txt", $query);

#$myaudio="http://libtech.avocadodesigns.in/exotel/audio/1004_anupds.wav";
#$myaudio="http://libtech.info/audio/1009_Bcastmah2905v2.wav";
?>
