<?php
$target_dir = "/Users/goli/Sites/libtech/a/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$imageFileType = pathinfo($target_file,PATHINFO_EXTENSION);

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
     echo "The file ". basename( $_FILES["fileToUpload"]["name"]). " has been uploaded.";
  } else {
      echo "Sorry, there was an error uploading your file.";
   }
}
?>
