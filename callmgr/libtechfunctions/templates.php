<?php

require_once(dirname(__FILE__).'/misc.php');
function test($mydbcon,$gid,$bid,$tid,$vid,$tfileid,$minhour,$maxhour){
    ltecho("Inside Test Broadcast".$tfileid);
    #$callparams='&fileid1='.$tfileid.'&fileid2=27503&fileid3=27503&fileid4=27503&fileid5=27503&ivrid=1';
    $callparams='&fileid1=37655&fileid2='.$tfileid.'&fileid3=27503&fileid4=27503&fileid5=27503&ivrid=1';
		$query="select phone,successrate from ghattu_ab where designation='goli' group by phone";
    #$query="select phone,successrate from addressbook where panchayat='test' or panchayat='Chodeya' or panchayat='losanga' or panchayat='tirrkela' or panchayat='lipingi' or panchayat='pondi' group by phone";
		$result = mysqli_query($mydbcon,$query);
		while ($row = mysqli_fetch_array($result)){
		  $phone=$row['phone'];
		$successrate=$row['successrate'];	
    $resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, successrate,bid, tid, vid,callparams,minhour,maxhour) VALUES
                ('".$phone."',".$successrate.",".$bid.",".$tid.",".$vid.",'".$callparams."',".$minhour.",".$maxhour.")");
		}
		
}


function chattis_weekly_broadcast($mydbcon,$gid,$bid,$tid,$vid,$tfileid,$minhour,$maxhour){
    ltecho("Inside Chattis Weekly Broadcast".$tfileid);
    $callparams='&fileid1='.$tfileid.'&fileid2=27503&fileid3=27503&fileid4=27503&fileid5=27503&ivrid=1';
  #  $callparams='&fileid1=37655&fileid2='.$tfileid.'&fileid3=27503&fileid4=27503&fileid5=27503&ivrid=1';
		$query="select phone,successrate from chattis_ab group by phone";
    #$query="select phone,successrate from addressbook where panchayat='test' or panchayat='Chodeya' or panchayat='losanga' or panchayat='tirrkela' or panchayat='lipingi' or panchayat='pondi' group by phone";
		$result = mysqli_query($mydbcon,$query);
		while ($row = mysqli_fetch_array($result)){
		  $phone=$row['phone'];
		$successrate=$row['successrate'];	
    $resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, successrate,bid, tid, vid,callparams,minhour,maxhour) VALUES
                ('".$phone."',".$successrate.",".$bid.",".$tid.",".$vid.",'".$callparams."',".$minhour.",".$maxhour.")");
		}
		
}


function chattis_pds_monthly($mydbcon,$gid,$bid,$tid,$vid,$tfileid,$minhour,$maxhour){
    ltecho("Inside Chattis Weekly Broadcast".$tfileid);
		//We get the month audio wave file no in tifileid
		$callparams='&fileid1=34415&fileid2=34418&fileid3='.$tfileid.'&fileid4=34419&fileid5=34416&fileid6=34418&fileid7='.$tfileid.'&fileid8=34419&fileid9=34417&fileid10=27503&fileid11=27503&fileid12=27503&fileid13=27503&fileid14=27503&fileid15=27503&fileid16=27503&fileid17=27503&fileid18=27503&fileid19=27503&fileid20=27503&ivrid=2';
		$query="select phone,successrate from chattis_ab group by phone";
		$result = mysqli_query($mydbcon,$query);
		while ($row = mysqli_fetch_array($result)){
		  $phone=$row['phone'];
		$successrate=$row['successrate'];	
    $resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, successrate,bid, tid, vid,callparams,minhour,maxhour) VALUES
                ('".$phone."',".$successrate.",".$bid.",".$tid.",".$vid.",'".$callparams."',".$minhour.",".$maxhour.")");
		}
		
}
function chattis_pds_monthly_feedback($mydbcon,$gid,$bid,$tid,$vid,$tfileid,$minhour,$maxhour){
    ltconsoleecho("Inside Chattis Feedback Calls".$tfileid);
		//We get the month audio wave file no in tifileid
		$callparams='chaupalwelcome have you picked rashan for january If you did not get rashan for january press one repeat have you picked rashan for january If you did not get rashan for january press one';
		$query="select phone,successrate from addressbook order by panchayat";
		$result = mysqli_query($mydbcon,$query);
		while ($row = mysqli_fetch_array($result)){
		  $phone=$row['phone'];
		$successrate=$row['successrate'];	
    $resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, successrate,bid, tid, vid,callparams,minhour,maxhour) VALUES
                ('".$phone."',".$successrate.",".$bid.",".$tid.",".$vid.",'".$callparams."',".$minhour.",".$maxhour.")");
		}
		
}
function anekapalli_weekly_broadcast($mydbcon,$gid,$bid,$tid,$vid,$tfileid,$minhour,$maxhour){
    ltecho("Inside ghattu weekly Broadcasts".$tfileid);
    $callparams='&fileid1='.$tfileid.'&fileid2=27503&fileid3=27503&fileid4=27503&fileid5=27503&ivrid=1';
		$query="select phone,successrate from anekapalli_ab";
  #  $query="select  phone,successrate from anekapalli_ab where block='Anakapalle';";
    $query="select phone,successrate from anekapalli_ab where block='Anantagiri' or block='Araku' or block='Chintapalli' or block='G.Madugula' or block='G.K. Veedhi' or block='Hukumpeta' or block='Koyyuru' or block='Munchingputtu' or block='Paderu' or block='Pedabayalu';";
    #$query="select phone,successrate from anekapalli_ab where block='Nathavaram';";
		#$query="select phone,successrate from ghattu_ab where panchayat='Yallamdoddi' or panchayat='test' or panchayat='aloor' or panchayat='ghattu'";
		$result = mysqli_query($mydbcon,$query);
		while ($row = mysqli_fetch_array($result)){
	  $phone=$row['phone'];
		$successrate=$row['successrate'];
    $resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, successrate,bid, tid, vid,callparams,minhour,maxhour) VALUES
                ('".$phone."',".$successrate.",".$bid.",".$tid.",".$vid.",'".$callparams."',".$minhour.",".$maxhour.")");
		}
		
}

function rscd_broadcast($mydbcon,$gid,$bid,$tid,$vid,$tfileid,$minhour,$maxhour){

    $callparams='&fileid1='.$tfileid.'&fileid2=27503&fileid3=27503&fileid4=27503&fileid5=27503&ivrid=1';
		$query="select phone,successrate from rscd_ab group by phone";
    $result = mysqli_query($mydbcon,$query);
		while ($row = mysqli_fetch_array($result)){
	  $phone=$row['phone'];
		$successrate=$row['successrate'];
    $resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, successrate,bid, tid, vid,callparams,minhour,maxhour) VALUES
                ('".$phone."',".$successrate.",".$bid.",".$tid.",".$vid.",'".$callparams."',".$minhour.",".$maxhour.")");
}
}

function apvvuVG_broadcast($mydbcon,$gid,$bid,$tid,$vid,$tfileid,$minhour,$maxhour){
    ltecho("Inside ghattu weekly Broadcasts".$tfileid);
    $callparams='&fileid1='.$tfileid.'&fileid2=27503&fileid3=27503&fileid4=27503&fileid5=27503&ivrid=1';
		$query="select phone,successrate from apvvuVG_ab";
    $result = mysqli_query($mydbcon,$query);
		while ($row = mysqli_fetch_array($result)){
	  $phone=$row['phone'];
		$successrate=$row['successrate'];
    $resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, successrate,bid, tid, vid,callparams,minhour,maxhour) VALUES
                ('".$phone."',".$successrate.",".$bid.",".$tid.",".$vid.",'".$callparams."',".$minhour.",".$maxhour.")");
		}
	}	

function ghattu_weekly_broadcast($mydbcon,$gid,$bid,$tid,$vid,$tfileid,$minhour,$maxhour){
    ltecho("Inside ghattu weekly Broadcasts".$tfileid);
    $callparams='&fileid1='.$tfileid.'&fileid2=27503&fileid3=27503&fileid4=27503&fileid5=27503&ivrid=1';
		$query="select phone,successrate from ghattu_ab";
    #$query="select phone,successrate from ghattu_ab where panchayat='thummalapalli' or panchayat='mittadoddi' or panchayat='balgera' or panchayat='macherla' or panchayat='Yallamdoddi' or panchayat='chintalakunta' or panchayat='Chagadona' or panchayat='Mallampalli' or panchayat='test';";
		#$query="select phone,successrate from ghattu_ab where panchayat='Yallamdoddi' or panchayat='test' or panchayat='aloor' or panchayat='ghattu'";
#    $query="select phone,successrate from ghattu_ab where panchayat='test' or panchayat='Chagadona' or panchayat='Lingapuram';";
   $result = mysqli_query($mydbcon,$query);
		while ($row = mysqli_fetch_array($result)){
	  $phone=$row['phone'];
		$successrate=$row['successrate'];
    $resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, successrate,bid, tid, vid,callparams,minhour,maxhour) VALUES
                ('".$phone."',".$successrate.",".$bid.",".$tid.",".$vid.",'".$callparams."',".$minhour.",".$maxhour.")");
		}
		
}
function basedongid($mydbcon,$gid,$bid){

    ltecho("Will try to retreive the playlist given the userid and vid");
		ltecho("Lets get all the users for hte particular grop".$gid);
		echo "Testing testing</br>";
	$vid=3;
	$tid=6;
  $resultUsr = mysqli_query($mydbcon,"SELECT * FROM Users LEFT JOIN UsersGroup
              ON UsersGroup.uid=Users.uid WHERE UsersGroup.gid=".$gid);
  while($rowUsr = mysqli_fetch_array($resultUsr)) {
//Inserting the cuntion here to retreive the playlist based on what needs to be played
    #$callparams='&fileid1=34069&fileid2=27503&fileid3=27503&fileid4=27503&fileid5=27503&ivrid=1';
    $callparams='&fileid1=34093&fileid2=32933&fileid3=34092&fileid4=32935&fileid5=27503&ivrid=1';
    $resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, bid, tid, vid,callparams) VALUES
                ('".$rowUsr['phone']."',".$bid.",".$tid.",".$vid.",'".$callparams."')");
  }
 

}
function ghattu_nrega($mydbcon,$gid,$bid,$tid){
    ltecho("Will try to retreive the playlist given the userid and vid");
		ltecho("Lets change the database and get the phone numbers and amount to be credited");
		$query="select * from apnrega_tocall order by household_code,disbursed_date";
		$query="select * from apnrega_tocall where apnregaid > 292 order by household_code,disbursed_date";
		$result = mysqli_query($mydbcon,$query);
		$prerow='';
		$i=0;
		
	 	$todaydate=date('d-M-Y');
		$payslipcount = 0;
		while($row = mysqli_fetch_array($result)) {
			$jobcard= $row['household_code'];
			$amount=$row['amount'];
			$paymentagency=$row['payingagency'];
			$bankdate=$row['bankdate'];
			$disbursed_date=$row['disbursed_date'];
			$datediff=getdiffdays($bankdate,$todaydate);
			$row['datediff']=$datediff;
			$phone=$row['phone'];
			if($i > 0){
				$payslipcount = $payslipcount + 1;
				//We will see if we want to concatenate the rows
				if(($prerow['household_code'] == $jobcard) && ($prerow['disbursed_date'] == $disbursed_date)){
					$row['amount'] = $amount + $prerow['amount'];
//					echo "We are Aggregating\n\n";
				}else{
					$amount=$prerow['amount'];
					$amountarray=genaudioarray($amount);
					echo "<b>2</b>".$amountarray[2]. "<b>1</b>".$amountarray[1]. "<b>0</b>".$amountarray[0]."  ".$amount."  </br>";
					if(count($amountarray) == 3){
							$money0=getfileid($mydbcon,$amountarray[0]);
							$money1=getfileid($mydbcon,$amountarray[1]);
							$money2=getfileid($mydbcon,$amountarray[2]);
							echo "<b>2</b>".$money2. "<b>1</b>".$money1. "<b>0</b>".$money0."  ".$amount."  </br>";
							}else{
							echo "Less than 1000 </br>";
							$money0=getfileid($mydbcon,$amountarray[0]);
							$money1=getfileid($mydbcon,$amountarray[1]);
							$money2=27503;
							}
					if(substr_count($prerow['disbursed_date'], '-') < 2){
						$calltype=1;
//We are only going to concentrate on this call right now.
							$fid1=33041;
							$fid2=getfileid($mydbcon,$payslipcount);//noofpayslips
							$fid3=33042;
							$fid4=$money0;//money
							$fid5=$money1;
							$fid6=$money2;
							$fid7=33043;
							$fid8=getfileid($mydbcon,$prerow['datediff']);//noofdaysbefore
							$fid9=33044;
							if(strpos($prerow['payingagency'],'ffice') !== false){
								$fid10=33194;//Combined file
								}else{
								$fid10=33193;//Combined file
							}
							$fid11=33201; 
							$fid12=$fid2; 
							$fid13=$fid3; 
							$fid14=$fid4; 
							$fid15=$fid5; 
							$fid16=$fid6; 
							$fid17=$fid7; 
							$fid18=$fid8; 
							$fid19=33044;
							$fid20=33200;
							$vid=3;
    					$playlist='&fileid1='.$fid1.'&fileid2='.$fid2.'&fileid3='.$fid3.'&fileid4='.$fid4.'&fileid5='.$fid5.'&fileid6='.$fid6.'&fileid7='.$fid7.'&fileid8='.$fid8.'&fileid9='.$fid9.'&fileid10='.$fid10.'&fileid11='.$fid11.'&fileid12='.$fid12.'&fileid13='.$fid13.'&fileid14='.$fid14.'&fileid15='.$fid15.'&fileid16=2'.$fid16.'&fileid17='.$fid17.'&fileid18='.$fid18.'&fileid19='.$fid19.'&fileid20='.$fid20.'&ivrid=2';
							echo $playlist."</br>";
							$query="INSERT INTO ToCall (phone, bid, tid, vid,callparams) VALUES
                ('".$prerow['phone']."',".$bid.",".$tid.",".$vid.",'".$playlist."')";
							echo $query."</br>";
						ltecho( "<b>".$calltype."   ".$payslipcount."  ".$prerow['bankdate']."   ".$prerow['datediff']."  ".$prerow['phone']."  ".$prerow['household_code']."   ".$prerow['amount']."</b>");
    					$resultTC = mysqli_query($mydbcon,"INSERT INTO ToCall (phone, bid, tid, vid,callparams) VALUES
                ('".$prerow['phone']."',".$bid.",".$tid.",".$vid.",'".$playlist."')");
						}else{
						$calltype=2;
					}
					echo "<b>".$calltype."   ".$payslipcount."  ".$prerow['bankdate']."   ".$prerow['datediff']."  ".$prerow['phone']."  ".$prerow['household_code']."   ".$prerow['amount']."</b>";
					for($j=0;$j<count($amountarray);$j++){
								echo $amountarray[$j]."  ";
						}
					$payslipcount = 0;
//					$aggamount = $prerow['amount'];
					echo "</br>";
					echo "\n";
				}
			}
			$i=$i+1;
			echo $phone."  ".$jobcard."  ".$amount."  ".$paymentagency."  ".$bankdate."  ".$disbursed_date."   ".$amount;
			echo "</br>";
			$prerow=$row;
			}
#    $playlist='&fileid1=28117&fileid2=28074&fileid3=27995&fileid4=28118&fileid5=27503';
    return $playlist;
}

?>
