
<?php
$htmlheader='
  <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <link rel="stylesheet" type="text/css" href="../css/basic.css">
</head>
';
print $htmlheader;
include ("./params.php");
$mydbcon = mysqli_connect("localhost",$dbuser,$dbpasswd);
if (!$mydbcon){
  print '<h3>ERROR ERROR Could not connect to DB ! Please contact webadmin</h3>';
}else{
        $query="use libtech";
        mysqli_query($mydbcon,$query);
        $name=$_POST['name'];
        $type=$_POST['broadcastType'];
        $tfileid=$_POST['tfileid'];
        $fileid=$_POST['fileid'];
        $block=$_POST['block'];
        $panchayats=$_POST['panchayat'];
        $groups=$_POST['groups'];
        $startDate=$_POST['startDate'];
        $endDate=$_POST['endDate'];
        $minhour=$_POST['minhour']; 
        $maxhour=$_POST['maxhour'];
        $groupString='';
        if($type == 'group'){
          foreach($groups as $group){
             $groupString.=$group.",";
          }
        }elseif($type =='geosurguja'){
          foreach($panchayats as $panchayat){
            $panchayatString.=$panchayat.",";
          }
        }
        
        $query="insert into broadcasts (name,type,startDate,endDate,minhour,maxhour,tfileid,fileid,groups,blocks,panchayats) values ('".$name."','".$type."','".$startDate."','".$endDate."',".$minhour.",".$maxhour.",'".$tfileid."','".$fileid."','".$groupString."','".$block."','".$panchayatString."');";
        mysqli_query($mydbcon,$query);
        $id=mysqli_insert_id($mydbcon);
        print "<h4>Congratulations !! Broadcast ".$name." added with ID ".$id."</h4>";
        
}

print '<h2><a href="./../html/broadcastsMain.html">Return to Main Broadcast Page</a></h2>';
