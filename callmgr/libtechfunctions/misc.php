<?php

function ltecho ($debug) {

$fileName="/tmp/libtech.log";
$datetime = date_create()->format('d-m-Y H:i:s');
if (file_exists($fileName)) {
        $fp = fopen($fileName, 'a+') ;
}
else {
        $fp = fopen($fileName, 'x+') ;
}
fwrite($fp,$datetime.":    ".$debug."\n");


}
function ltconsoleecho ($debug) {
echo $debug;
}

function getdiffdays($date1,$date2){
	 $dateint1=strtotime($date1);	
	 $dateint2=strtotime($date2);
	$days=($dateint2 - $dateint1)/86400;	
	return $days;
}
function ltopendb() {

 $con = mysqli_connect("localhost","root","ccmpProject**");
    if (!$con)
       {
      ltecho('Could not connect to DB');
      }

    if (mysqli_query($con,"USE libtech"))
      {
      ltecho('Database Opened libtech');
       }
    else
     {
     ltecho('Could not connect');
     }
   return $con;
}

function genaudioarray ($mynum){
$audioarray = array();
$divideby = 1000;
$remainder=$mynum % $divideby;
$number=explode('.',($mynum / $divideby));
$answer=$number[0];
if($answer != 0){
array_push($audioarray,$answer*1000);
}
$divideby = 100;
$number=explode('.',($remainder / $divideby));
$remainder1=$remainder % $divideby;
$answer=$number[0];
if($answer != 0){
array_push($audioarray,$answer*100);

}
if($remainder1 !=0){
array_push($audioarray,$remainder1);
}
return $audioarray;
}
function getfileid($mydbcon,$input){
		$query="select * from tring_ap_numbers where number=".$input;
		echo $query."</br>";
		$result = mysqli_query($mydbcon,$query);
		$row = mysqli_fetch_array($result);
		$output=$row['fileid'];
		return $output;
}

?>
