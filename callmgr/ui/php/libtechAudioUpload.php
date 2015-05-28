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
$query="use libtech";
mysqli_query($mydbcon,$query);

$target_dir = "/Users/goli/Sites/libtech/a/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$imageFileType = pathinfo($target_file,PATHINFO_EXTENSION);
$imageFileName = pathinfo($target_file,PATHINFO_FILENAME);

$filteredFileName= preg_replace('/[^a-zA-Z0-9]/i','',$imageFileName);
#print $fileName."<br>";
$query="insert into audioLibrary (name) values ('".$imageFileName."');";
#print $query;
mysqli_query($mydbcon,$query);
$id=mysqli_insert_id($mydbcon);
#print $id."</br>";
$fileName=$id."_".$filteredFileName.".wav";
$query="update audioLibrary set filename='".$fileName."' where id=".$id;
mysqli_query($mydbcon,$query);

$target_file=$target_dir.$fileName;

if (file_exists($target_file)) {
        echo "Sorry, file already exists.";
        $uploadOk = 0;
}
// Check file size
if ($_FILES["fileToUpload"]["size"] > 500000) {
            echo "Sorry, your file is too large.";
                $uploadOk = 0;
}

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
     print "<h4>The file ". basename( $_FILES["fileToUpload"]["name"]). " has been uploaded.</h4>";
     print "<h4>Your File ID is   ". $id.  " </h4>";
  } else {
      echo "Sorry, there was an error uploading your file.";
   }
}
?>
