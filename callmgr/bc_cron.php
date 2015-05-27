<?php
require_once(dirname(__FILE__).'/libtechfunctions/misc.php');
require_once(dirname(__FILE__).'/libtechfunctions/templates.php');
ltconsoleecho(" ");
ltconsoleecho(" ");
ltconsoleecho(" ");
ltconsoleecho("-------------------");
ltconsoleecho("EXECUTING BROADCAST CRON");
ltconsoleecho("-------------------");
$mydbcon = ltopendb();

$resultBC = mysqli_query($mydbcon,"SELECT * FROM Broadcasts WHERE processed=0 and vid=10 and startDate <= CURDATE();");
while($rowBC = mysqli_fetch_array($resultBC)) {
  ltconsoleecho("gid for broadcast: ".$rowBC['tid']);
  $gid=$rowBC['gid'];
	$bid=$rowBC['bid'];
	$tid=$rowBC['tid'];
	$vid=$rowBC['vid'];
	$minhour=$rowBC['minhour'];
	$maxhour=$rowBC['maxhour'];
	$tfileid=$rowBC['tfileid'];
  ltconsoleecho("File ID for broadcast: ".$tfileid);
  $resultFname=mysqli_query($mydbcon,"SELECT * FROM Templates WHERE tid=".$rowBC['tid']);
  ltconsoleecho("SELECT * FROM Templates WHERE tid=".$rowBC['tid']);
  $rowFname=mysqli_fetch_array($resultFname);
  $funcname=$rowFname['name'];
  ltconsoleecho($funcname);
  $funcstatus=$funcname($mydbcon,$gid,$bid,$tid,$vid,$tfileid,$minhour,$maxhour);
  ltconsoleecho("Function for Broadcast with vid is ".$rowFname['name']."  ".$rowBC['vid']);
  ltconsoleecho("mark broadcast as processed");
  $updateBC = mysqli_query($mydbcon,"UPDATE Broadcasts SET processed=1 where bid=".$rowBC['bid']);
}
?>
