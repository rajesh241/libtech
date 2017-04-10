<?php

function fetchOptions($mydbcon, $query,$database){
$query1="use ".$database;
mysqli_query($mydbcon,$query1);
$results=mysqli_query($mydbcon,$query);
$options="";
while($row=mysqli_fetch_array($results)){
    $options.='<option value="'.strtolower($row["name"]).'">'.strtolower($row["name"]).'</option>';
}//While loop ends
return $options;
}
function panchayatOptions($mydbcon){
$query="use surguja";
$options="";
mysqli_query($mydbcon,$query);
$query="select blockCode,name from blocks where isActive=1";        
$results=mysqli_query($mydbcon,$query);
while($row=mysqli_fetch_array($results)){
  $blockCode=$row['blockCode'];
  $name=strtolower($row['name']);
  $options.='<div id="'.$name.'-options" class="hidden"><select multiple name="panchayat[]">';
  $query="select name from panchayats where isActive=1 and blockCode='".$blockCode."';";
  $panchresults=mysqli_query($mydbcon,$query);
  $options.='<option value="all">All</option>';
  while($panchrow=mysqli_fetch_array($panchresults)){
    $panchayat=strtolower($panchrow['name']);
    $options.='<option value="'.$panchayat.'">'.$panchayat.'</option>';
  }//Panchayat While Block
  $options.='</select></div>';

}//While Block Loop
return $options;
}
?>
