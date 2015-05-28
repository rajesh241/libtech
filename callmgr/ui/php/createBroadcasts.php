<?php

include ("/Users/goli/params.php");
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
//Getting Surguja Block and Panchayat Names
$query="select name from blocks where isActive=1";
$surgujaBlockOptions=fetchOptions($mydbcon,$query,"surguja");
$panchayatOptions=panchayatOptions($mydbcon);
?>

<html>
  <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <link rel="stylesheet" type="text/css" href="../css/basic.css">
          <script src="../scripts/jquery.min.js">
          </script>
    
          <script language="javascript" type="text/javascript">
            $(function(){
        
              $("#broadcast-options").on("change", function() {
            
                $("#"+$(this).val()+"-table").removeClass("hidden").siblings("table").addClass("hidden")
            
              })
            
              $("#block-options").on("change", function() {
            
                $("#"+$(this).val()+"-options").removeClass("hidden").siblings("div").addClass("hidden")
        
              })
        
            });
          </script>
          <title>
            Create Edit Broadcasts 
          </title>

  </head>
        <h1> Create or Edit Broadcasts </h1>
        <form action="./../php/broadcastRequest.php" method="POST">
        <table  >
                <tbody>
                        <tr>
                                <td>Name of Broadcast 
                                </td>
                                <td>
                                        <input name="name" type="text" size="50"></input>
                                </td>
                        </tr>        
                        <tr>
                                <td>Type of Operation
                                </td>
                                <td>
                                        <select name="operation">
                                                <option value="new" selected>New Broadcast </option>
                                                <option value="edit" >Edit Existing Broadcast </option>
                                        </select>
                                </td>
                                </tr>    	  
                                <tr>
                                  <td>Type of Broadcast
                                  </td>
                                  <td><select name="broadcast-type" id="broadcast-options">
                                <option value="group" selected>Group</option>
                                <option value="geosurguja">Location Specific Chattisgarh</option>
                                  </td>
                          </tr>
                          <tr>
                           <td colspan="2">
                             <table id="group-table">
                               <tbody>
                                <tr>
                                  <td>
                                    Group Name
                                  </td>
                                  <td>
                                           <?php print $groupoption ?>

                                  </td>
                                </tr>
                              </tbody>
                      
                              </table>
                              
                              <table id="geosurguja-table" class="hidden">
                             	<tbody>
                             	  <tr>
                             	    <td>Block Name
                             	    </td>
                             	    <td><select  name="block" id="block-options" >
			                             <option value="0" selected>--Select-One--</option>
                                <?php print $surgujaBlockOptions ?>
                             	      </select>
                             	    </td>
                             	  </tr>
                                <tr>
		                              <td>Panchayat Name: पंचायत का नाम
		                              </td>
		                              <td>
		                                   <div id="panchayat-options" >
			                                   <select multiple name="panchayat[]" id="Default">
			                                     <option value="0" selected>--Select-One--</option>
			                                   </select>
                                      </div>
                                        <?php print $panchayatOptions ?>
		                                  </div>
		                                </td>
                                </tr>

                              	</tbody>
                                    </table>
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

    
</html>
