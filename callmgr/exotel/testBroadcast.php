<?php
header('Content-type: text/plain');
include ("./params.php");
$mydbcon = mysqli_connect("$dbserver",$dbuser,$dbpasswd);
$callid=$_GET["CallSid"];
#$callid='a325f1a0711dffa0d92163d6aa1ea2e2';
file_put_contents("/tmp/myget.txt", $callid);
$query="use libtech";
mysqli_query($mydbcon,$query);
#$query="select audio from callQueue where callid=".$callid;
$query="select filename from testBroadcast where sid='".$callid."'";
file_put_contents("/tmp/myget.txt", $query);
$result=mysqli_query($mydbcon,$query);
$row=mysqli_fetch_array($result);
$audio=$row['filename'];
$myaudio="http://callmgr.libtech.info/open/audio/".$audio."\n";
echo $myaudio;
?>
