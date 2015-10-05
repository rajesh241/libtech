
<?php
$htmlheader='
  <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <link rel="stylesheet" type="text/css" href="../css/basic.css">
</head>
';
print $htmlheader;
include ("./params.php");
$mydbcon = mysqli_connect($dbserver,$dbuser,$dbpasswd);
if (!$mydbcon){
  print '<h3>ERROR ERROR Could not connect to DB ! Please contact webadmin</h3>';
}else{
        $query="use libtech";
        mysqli_query($mydbcon,$query);
        $name=$_POST['name'];
        $type=$_POST['broadcastType'];
        $template=$_POST['broadcastTemplate'];
        $vendor=$_POST['vendor'];
        $tfileid=$_POST['tfileid'];
        $fileid=$_POST['fileid'];
        $fileid2=$_POST['fileid2'];
        $district=$_POST['district'];
        $block=$_POST['block'];
        $panchayats=$_POST['panchayat'];
        $groups=$_POST['groups'];
        $startDate=$_POST['startDate'];
        $endDate=$_POST['endDate'];
        $priority=$_POST['priority']; 
        $minhour=$_POST['minhour']; 
        $maxhour=$_POST['maxhour'];
        $groupString='';
        if($type == 'group'){
          foreach($groups as $group){
             $groupString.=$group.",";
          }
        }elseif($type =='location'){
          foreach($panchayats as $panchayat){
            $panchayatString.=$panchayat.",";
          }
        }
        $error=0;
        if( ($type == "group") && ($groupString == "")){
          $error=1;
          print "You have selected Group Broadcast but you have not selected any group";
        print "</br>";
        } 
        if( ($type == "location") && (($panchayatString == "") || ($block == "") || ($district == ""))){
          $error=1;
          print "You have selected Location based Broadcast but it seems that you have not selected district, block, panchayat, you would need to select all the three ";
          print "</br>";
          print "Please note that if you want to broadcast to all the panchayats, you would have to select all panchayats in the panchayat select";
          print "</br>";
        }
        if( ($vendor == "any") && (($fileid == "") || ($tfileid == ""))){
          print "Since you have selected vendor as any you would have to give both Tringo file ID and Libtech File ID";
          print "</br>";
          $error=1;
        }
        if( ($vendor == "exotel") && ($fileid == "") ){
          print "Since you have selected vendor as exotel you have not given Libtech File ID";
          print "</br>";
          $error=1;
        }
        if( ($vendor == "tringo") && ($tfileid == "") ){
          print "Since you have selected vendor as tringo you have not given Tringo File ID";
          print "</br>";
          $error=1;
        }
        if($error == 0){ 
        $query="insert into broadcasts (priority,name,vendor,type,template,startDate,endDate,minhour,maxhour,tfileid,fileid,fileid2,groups,district,blocks,panchayats) values (".$priority.",'".$name."','".$vendor."','".$type."','".$template."','".$startDate."','".$endDate."',".$minhour.",".$maxhour.",'".$tfileid."','".$fileid."','".$fileid2."','".$groupString."','".$district."','".$block."','".$panchayatString."');";
        mysqli_query($mydbcon,$query);
        $id=mysqli_insert_id($mydbcon);
        print "<h4>Congratulations !! Broadcast ".$name." added with ID ".$id."</h4>";
        }
        else{
          print "<h3> Broadcast not scheduled. Please clear above errors and submit again </h3>";
          print "</br>";
        }
}

print '<h2><a href="./../html/broadcastsMain.html">Return to Main Broadcast Page</a></h2>';
