<?php

include ("./params.php");
require_once(dirname(__FILE__).'/uifunctions.php');
$operation=$_POST['operation'];
$mydbcon = mysqli_connect("localhost",$dbuser,$dbpasswd);
$query="use libtech";
mysqli_query($mydbcon,$query);
//Getting Option value for all groups
$query="select id,name from groups where isActive=1";
$results=mysqli_query($mydbcon,$query);
$groupoption="";
while($row=mysqli_fetch_array($results)){
        #$groupoption.='<option value="'.$row["id"].'" >'.$row["name"].'</option>';
        $groupoption.='<input type="checkbox" name="groups[]" value="'.$row["id"].'">'.$row["name"].'<br>';
}//While loop ends
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" dir="ltr" lang="en">
<head>
	<title>Libtech Create Broadcasts</title>
  <link rel="stylesheet" type="text/css" href="../css/basic.css">
	<script type="text/javascript" src="../scripts/jquery-1.4.2.js"></script>
	<script type="text/javascript">

		$(document).ready(function() {
		$('#loader').hide();
	
		$('#district').change(function(){

			$('#block').fadeOut();
			$('#loader').show();

			$.post("./ajax_block.php", {
				district: $('#district').val()
			}, function(response){
				setTimeout("finishAjax('block', '"+escape(response)+"')", 400);
			});
			return false;
		});

		$('#block').change(function(){

			$('#panchayat').fadeOut();
			$('#loader').show();

			$.post("./ajax_panchayat.php", {
				district: $('#district').val(),
				block: $('#block').val()
			}, function(response){
				setTimeout("finishAjax('panchayat', '"+escape(response)+"')", 400);
			});
			return false;
		});

		});

		function finishAjax(id, response){
	 	 $('#loader').hide();
	 	 $('#'+id).html(unescape(response));
	 	 $('#'+id).fadeIn();
		}
	</script>
</head>
<body>
<div id="loader"><strong>Loading...</strong></div>
<h1> Create or Edit Broadcasts </h1>
<form name="theform" id="form" method="POST" action="./../php/broadcastRequest.php">

<table  >
                <tbody>
                        <tr>
                                <td>Name of Broadcast 
                                </td>
                                <td>
                                        <input required name="name" type="text" size="50"></input>
                                </td>
                        </tr>        
                        <tr>
                                <td>Type of Operation
                                </td>
                                <td>
                                        <select name="operation">
                                                <option value="new" selected>New Broadcast </option>
                                        </select>
                                </td>
                                </tr>    	  
                                <tr>
                                  <td>Type of Broadcast
                                  </td>
                                  <td><select name="broadcastType" id="broadcast-options">
                                <option value="group" selected>Group</option>
                                <option value="location">Location </option>
                                  </td>
                          </tr>
       <tr>
                                  <td>Broadcast Template
                                  </td>
                                  <td><select name="broadcastTemplate" >
                                <option value="general" selected>General Broadcast</option>
                                <option value="feedback">Feedback Broadcast </option>
                                  </td>
                          </tr>

                          <tr>
                                  <td>Select Vendor
                                  </td>
                                  <td><select name="vendor" >
                                <option value="any" selected>Any</option>
                                <option value="tringo" >Tringo</option>
                                <option value="exotel" >exotel</option>
                                  </td>
                          </tr>

                <tr>
                                <td>Tringo File ID (You can give multiple file IDs seperated by comma) 
                                </td>
                                <td>
                                        <input  name="tfileid" type="text" size="50"></input>
                                </td>
                        </tr>        
                        <tr>
                                <td>Libtech File ID (You can give multiple file IDs seperated by comma)
                                </td>
                                <td>
                                        <input  name="fileid" type="text" size="50"></input>
                                </td>
                        </tr>        
                        <tr>
                                <td>Start Date (The Date on which you want to start Broadcast)  
                                </td>
                                <td>
                                        <input required name="startDate" type="date" ></input>
                                </td>
                        </tr>
                        <tr>
                                <td>End Date  (System will keep trying to deliver the message till this date)
                                </td>
                                <td>
                                        <input required name="endDate" type="date" ></input>
                                </td>
                        </tr>
                             <tr>
                                <td>Priority (You can set the priority of the call, 1 is default, 10 is highest, For general Broadcasts 1 is a good value, for meeting request you can set it to 5. For extremely urgent Broadcasts you can set it to 10
                                </td>
                                <td>
                                        <select name="priority">
                                                <option value="1" selected >1 </option>
                                                <option value="2" >2 </option>
                                                <option value="3" >3 </option>
                                                <option value="4" >4 </option>
                                                <option value="5" >5 </option>
                                                <option value="6" >6 </option>
                                                <option value="7" >7 </option>
                                                <option value="8" >8 </option>
                                                <option value="9" >9 </option>
                                                <option value="10" >10 </option>
                                        </select>
                                </td>
                        </tr>

                        <tr>
                                <td>Minimum Hour (Calls will not go before this hour) 
                                </td>
                                <td>
                                        <select name="minhour">
                                                <option value="6" >06 </option>
                                                <option value="7" >07 </option>
                                                <option value="8" selected>08 </option>
                                                <option value="9" >09 </option>
                                                <option value="10" >10 </option>
                                                <option value="11" >11 </option>
                                                <option value="12" >12 </option>
                                                <option value="13" >13 </option>
                                                <option value="14" >14 </option>
                                                <option value="15" >15 </option>
                                                <option value="16" >16 </option>
                                                <option value="17" >17 </option>
                                                <option value="18" >18 </option>
                                                <option value="19" >19 </option>
                                                <option value="20" >20 </option>
                                        </select>
                                </td>
                        </tr>
                        <tr>
                                <td>Maximum Hour (Calls will not go after this hour) 
                                </td>
                                <td>
                                        <select name="maxhour">
                                                <option value="6" >06 </option>
                                                <option value="7" >07 </option>
                                                <option value="8" >08 </option>
                                                <option value="9" >09 </option>
                                                <option value="10" >10 </option>
                                                <option value="11" >11 </option>
                                                <option value="12" >12 </option>
                                                <option value="13" >13 </option>
                                                <option value="14" >14 </option>
                                                <option value="15" >15 </option>
                                                <option value="16" >16 </option>
                                                <option value="17" >17 </option>
                                                <option value="18" >18 </option>
                                                <option value="19" >19 </option>
                                                <option value="20" selected>20 </option>
                                        </select>
                                </td>
                        </tr>
                        <tr>
                                  <td>Select the Groups (THIS FIELD IS VALID ONLY IF BROADCAST TYPE IS GROUP)
                                  </td>
                                  <td>
                                           <?php print $groupoption ?>
                                  </td>
                          </tr>
                           <tr>
                                <td>District (THIS FIELD IS VALID ONLY IF BROADCAST TYPE IS LOCATION)

                                </td>
                             <td >
		<select id="district" name="district">
			<option value="">-- Select District --</option>
			<?php
	      $query="SELECT district FROM districts ORDER BY district ASC";
        $q=mysqli_query($mydbcon,$query);
				while($row = mysqli_fetch_array($q))
				{
					echo '<option value="'.$row['district'].'">'.$row['district'].'</option>';
				}
			?>
    </select>
</td>
                        </tr>
<tr>
                                <td>Block  (THIS FIELD IS VALID ONLY IF BROADCAST TYPE IS LOCATION)
                                </td>
<td>
		<select id="block" name="block">
			<option value="">-- Select Block --</option>
    </select>
</td>
                        </tr>
<tr>
                                <td>Panchayat  (THIS FIELD IS VALID ONLY IF BROADCAST TYPE IS LOCATION)
                                </td>
<td>

		<select multiple name="panchayat[]" id="panchayat">
			<option value="">-- Select panchayat --</option>
		</select>
</td>
</tr>
           <tr>
                             <td colspan="2" align="center">
                               <button type="submit">Submit</button>
                             </td>
                     </tr>

             </tbody>               
      </table>
</form>
</body>
</html>
