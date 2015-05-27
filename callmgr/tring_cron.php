<?php

require_once(dirname(__FILE__).'/libtechfunctions/misc.php');
$vid=10; //Vendor ID for tring is 3
$maxretry=10;
//Tring URL
$tringurl='http://hostedivr.in/netobd/NewCall_Schedule.php?uid=523&pwd=golani123&pno=9845065241&fileid1=27667&fileid2=27503&fileid3=27503&fileid4=27503&fileid5=27503';
$tringstatusurl='http://www.hostedivr.in/netobd/fetchCallRecord.php?uid=523&pwd=golani123&callreqid=';
ltecho(" ");
ltecho(" ");
ltecho(" ");
ltecho("-------------------");
ltecho("EXECUTING TRING CRON");
ltecho("-------------------");
$mydbcon = ltopendb();
ltecho("First will check the status of previous placed calls");
ltecho(" ");

$query="select vendorcallid,bid,cid,phone,tid,retry,callparams,TIMESTAMPDIFF(MINUTE, callRequestTime, now()) tdiff from ToCall where inprogress=1 AND vid=".$vid;
ltecho($query);
$result = mysqli_query($mydbcon,$query);
while($row = mysqli_fetch_array($result)) {
		$bid=$row['bid'];
		$callparams=$row['callparams'];
		$vendorcid=$row['vendorcallid'];
		$timediff=$row['tdiff'];
    ltecho("TIME DIFF=".$timediff."CID=".$row['cid']."VENDORCALLID=".$row['vendorcallid']);
    $tringlog=file_get_contents($tringstatusurl.$row['vendorcallid']);
    $tringlogarray=explode("|",$tringlog);
    $tringstatus=$tringlogarray[5];
    $debug="Status,callnumber ".$tringlogarray[0]."-".$tringstatus[2]." ";
    ltecho("DEBUGGING");
    ltecho($tringlog);
    ltecho($tringstatus);
    $retry=$row['retry'];
    $success=0;
		$duration=0;
		//First of all from Tring Status we need to find out if call has been completed or not
		if( preg_match('(COMPLETE|INCOMPLETE)', $tringstatus)){
			$callinprogress = "NO";
#		}else if(($timediff > 30 ) && ($tringstatus == "CONNECTED") ){//If the time difference since the call was initialted is greater than 1 hour then mark the call as error
#			$callinprogress ="UNKNOWN";
		}else if( preg_match('(NEW CALL|CALL INITIATED|DIALING|CONNECTED|SCHEDULED)', $tringstatus)){
			$callinprogress ="YES";
		}else{
			$callinprogress = "UNKNOWN";
		}
    ltecho("Call InProgess  ".$callinprogress);
		//Now lets measure success
  	if($tringstatus == "COMPLETE"){
      	$duration=strtotime($tringlogarray[4])-strtotime($tringlogarray[3]);
        if($duration > 15){
           $success=1;
        }
        $ctime=$tringlogarray[3];
      }else if(($tringstatus == "INCOMPLETE") && ($retry == 0)){
        $success=2;
        $ctime=$tringlogarray[2];
			}else if($callinprogress == "UNKNOWN"){
				$success=3;//ERROR
        $ctime=$tringlogarray[2];
			}
    ltecho("Call SUCCESS ".$success);
	  //Now lets us update ToCall, if call inprogress is yes then we dont have to update to call
    if($callinprogress != "YES"){
			if( ($success==0) || ($success==3)){
      $insquery="update ToCall set inprogress=0,debug='".$debug."',success=".$success." where cid=".$row['cid'];
      ltecho($insquery);
      $insresult = mysqli_query($mydbcon,$insquery);
			}else{
			//We need to delete from ToCall
      $insquery="delete from ToCall where cid=".$row['cid'];
      ltecho($insquery);
      $insresult = mysqli_query($mydbcon,$insquery);
        //Now we need to update the callStatus table
        $attempts=$maxretry-$retry;
        if($success==1){
          $insquery="insert into callStatus (phone,success,bid,attempts) values ('".$row['phone']."',1,".$bid.",".$attempts.");";
          ltecho($insquery);
          $insresult = mysqli_query($mydbcon,$insquery);
        }elseif($success==2){
          $insquery="insert into callStatus (phone,maxRetryFail,bid,attempts) values ('".$row['phone']."',1,".$bid.",".$attempts.");";
          ltecho($insquery);
          $insresult = mysqli_query($mydbcon,$insquery);
        }

			}
		}
		//Now we need to update CompletedCalls in case if the call is not in progress
		if($callinprogress != "YES"){
    ltecho("Duration".$duration." Calltime".$ctime);
    $insquery="insert into CompletedCalls (vendorcid,callparams,phone,bid,tid,vid,success,ctime,duration,debug) values ('".$vendorcid."','".$callparams."','".$row['phone']."',".$bid.",".$row['tid'].",".$vid.",".$success.",'".$ctime."',".$duration.",'".$debug."')";
    ltecho($insquery);
    $insresult = mysqli_query($mydbcon,$insquery);
		}
	
	}//While Loop for call in Progress
/*	
    if($tringstatus == "COMPLETE"){
        $success=1;
        $ctime=$tringlogarray[3];
      }else if(($tringstatus == "INCOMPLETE") && ($retry == 0)){
        $success=2;
        $ctime=$tringlogarray[2];
      }else if (preg_match('(JPG|jpg|png|jpeg|gif|bmp)', $tringstatus)){
				$callinprogress=1;
			}
		//Now update ToCall. If retry =0, or success=1 we need to remove it from the ToCall register.
    if(($success ==1) || ($retry==0)){
      $duration=strtotime($tringlogarray[4])-strtotime($tringlogarray[3]);
      $insquery="delete from ToCall where cid=".$row['cid'];
      ltecho($insquery);
      $insresult = mysqli_query($mydbcon,$insquery);
      }else{
      $ctime=$tringlogarray[2];
      $duration=0;
      $insquery="update ToCall set inprogress=0,debug='".$debug."',success=".$success." where cid=".$row['cid'];
      ltecho($insquery);
      $insresult = mysqli_query($mydbcon,$insquery);
      }
    ltecho("Duration".$duration." Calltime".$ctime);
    $insquery="insert into CompletedCalls (callparams,phone,bid,tid,vid,success,ctime,duration,debug) values ('".$callparams."','".$row['phone']."',".$bid.",".$row['tid'].",".$vid.",".$success.",'".$ctime."',".$duration.",'".$debug."')";
    ltecho($insquery);
    $insresult = mysqli_query($mydbcon,$insquery);
    }*/

ltecho("Lets Place New calls");
$query="select * from ToCall where inprogress=1 and vid=".$vid;
ltecho($query);
$result = mysqli_query($mydbcon,$query);
$queuedcalls = mysqli_num_rows($result);
ltecho("QUEUED CALLS ".$queuedcalls);
$curhour=date('H');
ltecho("Current Hour".$curhour);
if(($curhour >= 6) && ($curhour < 21) && ($queuedcalls < 20)){
ltecho("Time check passed and the Queued calls seem to be less than 10");
#$query="select cid,callparams,phone,tid,retry from ToCall where success=0 AND inprogress=0 AND minhour <= ".$curhour." AND maxhour > ".$curhour. " AND vid=".$vid." ORDER BY retry DESC,successrate DESC LIMIT 25";
$query="select tc.cid,tc.callparams,tc.phone,tc.tid,tc.retry from ToCall tc, Broadcasts b where tc.bid=b.bid and b.endDate >= CURDATE()  and tc.success=0 AND tc.inprogress=0 AND tc.minhour <= ".$curhour." AND tc.maxhour > ".$curhour. " AND tc.vid=".$vid." ORDER BY tc.retry DESC,tc.successrate DESC LIMIT 25";
ltecho($query);
$result = mysqli_query($mydbcon,$query);
while($row = mysqli_fetch_array($result)) {
    ltecho($row['cid'].$row['phone'].$row['tid']);
    ltecho($row['callparams']);
    $vendorcallid = 17;
    $tringurl='http://hostedivr.in/netobd/NewCall_Schedule.php?uid=523&pwd=golani123&pno='.$row['phone'].$row['callparams'];
    ltecho($tringurl); 
    $vendorcallid = file_get_contents($tringurl);
    if(preg_match("/[0-9]/", $vendorcallid)) {
    $retry=$row['retry'] -1;
    $insquery="update ToCall set inprogress=1,callRequestTime=NOW(),retry=".$retry.",vendorcallid=".$vendorcallid." where cid=".$row['cid'];
    ltecho($insquery);
    $insresult = mysqli_query($mydbcon,$insquery);
    }//If PREG Match
  }//While Loop
}//if TIME

ltecho("");
ltecho("");
ltecho("");

?>
