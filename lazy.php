<?php

include 'verify.php';

/* if (!verify_session()) {die();} */

$PATH = './ram/';
header('Content-Type: text/javascript');

$files = scandir($PATH);
$array_sorted = array();
foreach ($files as $file) {
    if ($file != '.' || $file != '..') {
        array_push($array_sorted, (int)$file);
    }
}
rsort($array_sorted);

$file = fopen($PATH. $array_sorted[0], "r") or die("Unable to open file!");

$_ = trim(fgets($file));
$_ = trim(fgets($file));
$_ = fgets($file);
$reports_search = trim(fgets($file));
$reports_data = trim(fgets($file));
fclose($file);
echo "let reports_search = " . $reports_search . ";\n";
echo "let reports_data = " . $reports_data . ";\n";

$lazy = fopen("lazy.js", "r") or die("Unable to open file!");
$script = fread($lazy, filesize("lazy.js"));
echo $script;
fclose($lazy);
?>
