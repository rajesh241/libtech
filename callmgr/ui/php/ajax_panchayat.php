<?php
include ("./params.php");
require_once(dirname(__FILE__).'/uifunctions.php');
$mydbcon = mysqli_connect("localhost",$dbuser,$dbpasswd);
$query="use libtech";
mysqli_query($mydbcon,$query);
	if(isset($_POST['district']) && isset($_POST['block']))
	{
		$block = $_POST['block'];
		$district = $_POST['district'];
		
		$option .= '<option value="all">All Panchayats</option>';
		$query = "SELECT panchayat FROM panchayats WHERE district = '$district' AND block = '$block' ORDER BY panchayat ASC";
    $q=mysqli_query($mydbcon,$query);
		while($row = mysqli_fetch_array($q))
		{
			$option .= '<option value="' . $row['panchayat'] . '">' . $row['panchayat'] . '</option>';
		}
		
		echo $option;
	}
?>
