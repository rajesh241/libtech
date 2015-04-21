<?php

function genpanchreport($mydbcon,$addressbook,$bid){
echo "In generate Panchayat Report</br>";

$query="select ".$addressbook.".panchayat from CompletedCalls,".$addressbook." where ".$addressbook.".phone=CompletedCalls.phone AND bid=".$bid." group by ".panchayat;";
}
?>
