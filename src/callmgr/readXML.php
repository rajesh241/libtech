<?php
$curdir=realpath(dirname(__FILE__));
print $curdir;
include ($curdir."/../includes/params.php");
$mydbcon = mysqli_connect("$dbserver",$dbuser,$dbpasswd);
$xmlkeys=array('missedCallID', 'phone', 'ts','jobcard', 'isUpdate','htmlgen','payOrderList', 'workerID', 'name', 'complaintNumber', 'complaintDate', 'problemType', 'periodInWeeks', 'remarks', 'rdCallCenterStatus', 'redressalRemarks', 'currentStep', 'finalStatus', 'closureReason');
#Escaping mysql $city = $mysqli->real_escape_string($city);
//Opening Database
# $mydbcon = mysqli_connect("localhost","root","ccmpProject**");
    if (!$mydbcon)
       {
      echo('Could not connect to DB');
      }

    if (mysqli_query($mydbcon,"USE libtech"))
      {
      echo('Database Opened libtech');
       }
    else
     {
     echo('Could not connect');
     }
 
#$query="select vendorcallid,bid,cid,phone,tid,retry,callparams from ToCall where inprogress=1 AND vid=".$vid;
#$result = mysqli_query($mydbcon,$query);
#while($row = mysqli_fetch_array($result)) {
$files = scandir($xmldir);
if(count($files) > 2){
foreach ($files as $onefile){
  if (strpos($onefile,'.xml') !== false) {
          $fileParts=explode("_", $onefile);
          $id=$fileParts[0];  
          $phone=$fileParts[1];  
          $tsparts=explode(".",$fileParts[2]); 
          $ts=$tsparts[0];
          echo $id."  ".$phone."  ".$ts."\n";
          echo $onefile;
          #Now we need to check if this update has been already recorded or not
          $query="select id from ghattuMissedCallsLog where missedCallID=".$id." and phone='".$phone."' and ts=".$ts.";";
          print $query;
          $result = mysqli_query($mydbcon,$query);
          if(mysqli_num_rows($result) == 0){
          $doc = new DOMDocument(); 
          $doc->load( $xmldir.$onefile ); 
   
          $jobcards = $doc->getElementsByTagName( "greivanceUpdate" ); 
          foreach( $jobcards as $jobcard ) 
          {
            $keystring="(";
            $keyvaluestring="(";
            foreach($xmlkeys as $key){
            $keyvalues = $jobcard->getElementsByTagName( $key ); 
            $keyvalue = $keyvalues->item(0)->nodeValue; 
                echo $key."+".$keyvalue."\n";
            $keystring.=$key.","; 
            $keyvaluestring.="'".$mydbcon->real_escape_string($keyvalue)."',"; 
            }
            echo "\n\n\n\n";
            echo $keystring;
            echo $keyvaluestring;
            echo "\n\n\n\n";
            $query="insert into ghattuMissedCallsLog ".rtrim($keystring, ",").") values ".rtrim($keyvaluestring,",").");";
            $result = mysqli_query($mydbcon,$query);
            echo $query;
            $query="delete from ghattuMissedCallsLog where missedCallID=0";
            $result = mysqli_query($mydbcon,$query);
            echo "\n\n\n\n";
          } 
       }//If mysqli rows is equal to zero

  }//IF File is XML
}//For Each
}//If Count



  ?>
