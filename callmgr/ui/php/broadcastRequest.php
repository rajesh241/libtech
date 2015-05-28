
<?php
$htmlheader='
  <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <link rel="stylesheet" type="text/css" href="../css/basic.css">
</head>
';
print $htmlheader;
include ("/Users/goli/params.php");
$mydbcon = mysqli_connect("localhost",$dbuser,$dbpasswd);
if (!$mydbcon){
  print '<h3>ERROR ERROR Could not connect to DB ! Please contact webadmin</h3>';
}else{
        $blocks=$_POST['block'];
        $panchayats=$_POST['panchayat'];
        $groups=$_POST['groups'];
        print_r($blocks);
        print_r($panchayats);
        print_r($groups);
}
