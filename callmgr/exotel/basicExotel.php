<?php
header('Content-type: text/plain');
include ("./params.php");
$mydbcon = mysqli_connect("$dbserver",$dbuser,$dbpasswd);
$callid=400102;
$callid=$_GET["CustomField"];
file_put_contents("/tmp/myget.txt", $callid);
$query="use libtech";
mysqli_query($mydbcon,$query);
$query="select audio from callQueue where callid=".$callid;
#$query="select audio from callQueue where id=5";
$result=mysqli_query($mydbcon,$query);
$row=mysqli_fetch_array($result);
$audio=$row['audio'];
$audioarray=explode(",",$audio);
foreach($audioarray as $singleaudio){
$myaudio="http://callmgr.libtech.info/open/audio/".$audio."\n";
#$myaudio="http://libtech.info/audio/".$singleaudio."\n";
echo $myaudio;
}
#file_put_contents("/tmp/myget.txt", $query);

#$myaudio="http://libtech.avocadodesigns.in/exotel/audio/1004_anupds.wav";
#$myaudio="http://libtech.info/audio/1009_Bcastmah2905v2.wav";
?>
