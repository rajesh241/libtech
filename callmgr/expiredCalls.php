<?php

require_once(dirname(__FILE__).'/libtechfunctions/misc.php');
$vid=10; //Vendor ID for tring is 3
$maxretry=10;

ltecho("Marking Expired Calls");
ltecho("-------------------");
$mydbcon = ltopendb();
$query="select tc.vid,tc.bid,tc.cid,tc.callparams,tc.phone,tc.tid,tc.retry from ToCall tc, Broadcasts b where tc.bid=b.bid and b.endDate < CURDATE()   AND tc.inprogress=0  ;";
ltecho($query);
$result = mysqli_query($mydbcon,$query);
while($row = mysqli_fetch_array($result)) {
  $cid=$row['cid'];
  $bid=$row['bid'];
  $vid=$row['vid'];
  $phone=$row['phone'];
  $retry=$row['retry'];
  $attempts=$maxretry-$retry;
  $insquery="insert into callStatus (bid,expired,phone,attempts) values (".$bid.",1,'".$phone."',".$attempts.");";
  ltecho($insquery);
  $insresult = mysqli_query($mydbcon,$insquery);
  $delquery="delete from ToCall where cid=".$cid;
  ltecho($delquery);
  $delquery = mysqli_query($mydbcon,$delquery);
}
?>
