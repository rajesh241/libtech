<?php

include ("./params.php");
require_once(dirname(__FILE__).'/uifunctions.php');
$mydbcon = mysqli_connect("localhost",$dbuser,$dbpasswd);
$query="use libtech";
mysqli_query($mydbcon,$query);


    if(isset($_POST['district']))
    {
		    $district = $_POST['district'];
        $option .= '<option value="">-- Select Block --</option>';
                
        $query="SELECT block FROM blocks WHERE district = '$district' ORDER BY block ASC";
        $q=mysqli_query($mydbcon,$query);
        while($row = mysqli_fetch_array($q))
        {
            $option .= '<option value="' . $row['block'] . '">' . $row['block'] . '</option>';
        }
        
        echo $option;
    }
?>
