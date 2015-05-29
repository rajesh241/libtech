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
print "<h1> List of All Audio Files </h1>";
include ("./params.php");
$operation=$_POST['operation'];
$mydbcon = mysqli_connect("localhost",$dbuser,$dbpasswd);
if (!$mydbcon){
  print '<h3>ERROR ERROR Could not connect to DB ! Please contact webadmin</h3>';
}else{
  $query="use libtech";
  mysqli_query($mydbcon,$query);
  $query="select id,name from audioLibrary order by ts desc";
  $results=mysqli_query($mydbcon,$query);
  print "<table>";
  print "<tr><th>File ID</th><th>File Name</th></tr>";
  while($row = mysqli_fetch_array($results)){
          print "<tr>";
    print "<td>".$row['id']."</td><td>".$row['name']."</td>";
    print "</tr>";
  }
  print "</table>";
  print $htmlfooter;
}//Main if else statement
?>