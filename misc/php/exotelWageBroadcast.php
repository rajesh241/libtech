<?php
header('Content-type: text/plain');
include ("./params.php");
$mydbcon = mysqli_connect($dbserver,$dbuser,$dbpasswd);
$callid=$_GET["CustomField"];
file_put_contents("/tmp/myget.txt", $callid);
$query="use libtech";
mysqli_query($mydbcon,$query);
$query="select audio from callQueue where callid=".$callid;
$result=mysqli_query($mydbcon,$query);
$row=mysqli_fetch_array($result);
$audio=$row['audio'];
#$audio="chattisgarh_wage_broadcast_static0,lundra,chattisgarh_wage_broadcast_static1,200,32,chattisgarh_wage_broadcast_static2,700,47,chattisgarh_wage_broadcast_static3,25,aug,chattisgarh_wage_broadcast_static4,chattisgarh_wage_broadcast_repeat,chattisgarh_wage_broadcast_static0,lundra,chattisgarh_wage_broadcast_static1,200,32,chattisgarh_wage_broadcast_static2,700,47,chattisgarh_wage_broadcast_static3,25,aug,chattisgarh_wage_broadcast_static4,chattisgarh_wage_broadcast_thankyou";
#$audio="chattisgarh_wage_broadcast_static0,ashkala,chattisgarh_wage_broadcast_static1,200,2,chattisgarh_wage_broadcast_static2,300,18,chattisgarh_wage_broadcast_static3,14,august,2015,chattisgarh_wage_broadcast_static4,chattisgarh_wage_broadcast_repeat,chattisgarh_wage_broadcast_static0,ashkala,chattisgarh_wage_broadcast_static1,200,2,chattisgarh_wage_broadcast_static2,300,18,chattisgarh_wage_broadcast_static3,14,august,2015,chattisgarh_wage_broadcast_static4,chattisgarh_wage_broadcast_thankyou";
#$audio="chattisgarh_wage_broadcast_static0,ashkala,chattisgarh_wage_broadcast_static1,85,chattisgarh_wage_broadcast_static2,300,18,chattisgarh_wage_broadcast_static3,14,august,2015,chattisgarh_wage_broadcast_static4,chattisgarh_wage_broadcast_repeat,chattisgarh_wage_broadcast_static0,ashkala,chattisgarh_wage_broadcast_static1,85,chattisgarh_wage_broadcast_static2,300,18,chattisgarh_wage_broadcast_static3,14,august,2015,chattisgarh_wage_broadcast_static4,chattisgarh_wage_broadcast_thankyou";
#$audio="chattisgarh_wage_broadcast_static0,lundra,chattisgarh_wage_broadcast_static1";
$audioarray=explode(",",$audio);
foreach($audioarray as $singleaudio){
$myaudio="http://libtech.info/audio/hindi/hindi_".$singleaudio.".wav\n";
echo $myaudio;
}
#file_put_contents("/tmp/myget.txt", $query);

#$myaudio="http://libtech.avocadodesigns.in/exotel/audio/1004_anupds.wav";
#$myaudio="http://libtech.info/audio/1009_Bcastmah2905v2.wav";
?>
