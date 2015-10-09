<?php
$htmlheader='
  <head>
          <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
          <link rel="stylesheet" type="text/css" href="../css/basic.css">
</head>
';
print $htmlheader;
include ("./params.php");
$mydbcon = mysqli_connect("localhost",$dbuser,$dbpasswd);
$query="use surguja";
mysqli_query($mydbcon,$query);
$workCode=$_POST['workCode'];
print $workCode;
$workCode=str_replace("/","_",$workCode);
$target_dir = "/tmp/";
$target_dir = $_SERVER["DOCUMENT_ROOT"]."/audio/workNames/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
//print $target_file;
//$target_file = $target_dir . $workCode.".wav";
$uploadOk = 1;
$imageFileType = pathinfo($target_file,PATHINFO_EXTENSION);
$fileName=$workCode.".wav";
$target_file=$target_dir.$fileName;
#print $target_file;
if (file_exists($target_file)) {
        echo "Sorry, file already exists.";
        $uploadOk = 0;
}
// Check file size
#if ($_FILES["fileToUpload"]["size"] > 500000) {
#            echo "Sorry, your file is too large.";
#                $uploadOk = 0;
#}

// Allow certain file formats
if($imageFileType != "wav"   ) {
                    echo "<h3>Sorry, only wav files are allowed.</h3>";
                        $uploadOk = 0;
}
// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
            echo "Sorry, your file was not uploaded.";
} else {
  if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
     //print "<h4>The file ". basename( $_FILES["fileToUpload"]["name"]). " has been uploaded.</h4>";
     $query="update works set isRecorded=1 where finyear='16' and workCode='".$_POST['workCode']."';";
     print "<h4> File Recorded Successfully. Thanks </h4>";
     mysqli_query($mydbcon,$query);
  } else {
      echo "Sorry, there was an error uploading your file.";
   }
}

     print '<h2><a href="./recordWorkNames.py">Return to Record Work Names</a></h2>';
?>
