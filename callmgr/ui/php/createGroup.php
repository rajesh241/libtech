<?php
$htmlheader='
  <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <link rel="stylesheet" type="text/css" href="../css/basic.css">
</head>
';
print $htmlheader;
include ("/Users/goli/params.php");
$operation=$_POST['operation'];
$mydbcon = mysqli_connect("localhost",$dbuser,$dbpasswd);
if (!$mydbcon){
  print '<h3>ERROR ERROR Could not connect to DB ! Please contact webadmin</h3>';
}else{
        $query="use libtech";
        mysqli_query($mydbcon,$query);
        $name=$_POST['name'];
        $description=$_POST['description'];
        if (preg_match('/^[a-zA-Z0-9 .\-]+$/i', $name)){
                //Validated the name of group not to have any special charactera
                $query="select * from groups where name='".$name."';";
                $norows=mysqli_query($mydbcon,$query);
                if((mysqli_num_rows($norows) == 0 ) || ($operation == 'append')){
                        $addNumbers=0;
                  if($operation == 'new'){
                    $query="insert into groups (name,description) values ('".$name."','".$description."');";
                    mysqli_query($mydbcon,$query);
                    print "<h4>Group successfully Created </h4>";
                    $addNumbers=1;
                  }else if(mysqli_num_rows($norows) ==1){
                          $addNumbers=1;
                  }else{
                   print "<h3> ERROR: You have requested to append numbers to group ".$name."But the group does not exist</h3>"; 
                  }
                  #We will add numbers if it is new group or if it is existing group and name exists
                  if($addNumbers == 1){
                    $allNumbers=$_POST['phoneNumbers'];
                    $phoneArray = preg_split('/\s+/', $allNumbers);
                    $i=0;
                    $uniquePhoneAdded=0;
                    $addedToGroup=0;
                    foreach($phoneArray as $phone){
                      $query="insert into addressbook (phone) values ('".$phone."');";
                      mysqli_query($mydbcon,$query);
                      $uniquePhoneAdded=mysqli_affected_rows($mydbcon)+$uniquePhoneAdded;
                      $namepattern="~".$name."~";
                      $query="update addressbook set groups=concat(ifnull(groups,''),'".$namepattern."') where phone='".$phone."' and groups not like '%".$namepattern."%';";
                      mysqli_query($mydbcon,$query);
                      $addedToGroup=mysqli_affected_rows($mydbcon)+$addedToGroup;
                      $query="update addressbook set groups='".$namepattern."' where phone='".$phone."' and groups is NULL";
                      mysqli_query($mydbcon,$query);
                      $addedToGroup=mysqli_affected_rows($mydbcon)+$addedToGroup;
                      #print $query;
                      $i=$i+1;
                      #print $i."   ".$phone;
                    }//For Each Loop
                    print "<h4> Phone Number Added ".$addedToGroup."</h4>";
                  } 
                }else{
                        print "<h3>The group name already exists, please try some other name</h3>";
                }
        }else{
                print "<h3>The name can contain only letters and numbers, no special characters allowed Please try again</h3>";
        }
}

