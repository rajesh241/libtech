<?php

function ftorejectedreport($mydbcon){
$file = fopen("fto1.csv","r");
$fileName="/tmp/rejected_transaction.csv";
if (file_exists($fileName)) {
        $fp = fopen($fileName, 'w+') ;
}
else {
        $fp = fopen($fileName, 'x+') ;
}
$i=0;
$writetofile="i,panchayatname,jobcard,name,phone,amount,transactiondate,processeddate,accountno,fto_no,refno,newfto_no,new_refno\n";	
fwrite($fp,$writetofile);
	echo $writetofile;
  echo "</br>";
while((! feof($file)) )
  {
	$i = $i +1;
  $oneline = fgetcsv($file);
	$jobcard=$oneline[0];
  $i=(int)$oneline[1];
	$fto_no=$oneline[2];
  $refno=$oneline[3];
	$name=$oneline[5];
  $amount=$oneline[11];
	$processeddate=$oneline[1];
	$reason=$oneline[12];
	$accountno=$oneline[7];
	$code=substr($jobcard,10,3);
	$query="select * from places where parentpid=64 and code='".$code."';";
	echo $query;
	$result1 = mysqli_query($mydbcon,$query);
	$row1=mysqli_fetch_array($result1);
	$panchayatname=$row1['name'];
	$query="select phone from addressbook where jobcard='".$jobcard."';";
  $result = mysqli_query($mydbcon,$query);
	$row=mysqli_fetch_array($result);
	$phone=$row['phone'];
	$newftono=$oneline[14];
	$newrefno=$oneline[13];
	$writetofile=$i.",".$panchayatname.",".$jobcard.",".$name.",".$phone.",".$amount.",".$reason.",".$processeddate.",".$accountno.",".$fto_no.",".$refno.",".$newftono.",".$newrefno."\n";	
	fwrite($fp,$writetofile);
	echo $writetofile;
  echo "</br>";

	
  }
 
}
?>
