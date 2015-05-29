<?php
$htmlheader='
  <html>
  <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <link rel="stylesheet" type="text/css" href="../css/basic.css">
</head>
';
$htmlfooter="</html>";
print $htmlheader;
print "<h1> List of All Groups  </h1>";
include ("./params.php");
$operation=$_POST['operation'];
$mydbcon = mysqli_connect("localhost",$dbuser,$dbpasswd);
if (!$mydbcon){
  print '<h3>ERROR ERROR Could not connect to DB ! Please contact webadmin</h3>';
}else{
  $query="use libtech";
  mysqli_query($mydbcon,$query);
  $query="select id,name,description from groups ";
  $results=mysqli_query($mydbcon,$query);
  print "<table>";
  print "<tr><th>Group ID</th><th>Group Name</th><th>Description</th><th>Subscribers</th></tr>";
  while($row = mysqli_fetch_array($results)){
    $query="select count(*) c from addressbook where groups like '%~".$row['name']."~%'";
    $results1=mysqli_query($mydbcon,$query);
    $row1 = mysqli_fetch_array($results1);
    print "<tr>";
    print "<td>".$row['id']."</td><td>".$row['name']."</td><td>".$row['description']."</td><td>".$row1['c']."</td>";
    print "</tr>";
  }
  print "</table>";
  print $htmlfooter;
}//Main if else statement
?>
