<?php
include 'verify.php';
/* if (!verify_session()){header('Location: /login.php');die();} */
?>

<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport"content="width=device-width,initial-scale=1"><title>R1 Search</title><link href="style.css"rel="stylesheet"></head><body><header><nav><div id="menu"><button id="agents_btn"class="agents_s"type="button"onclick="toggle_domain(0)">Agents</button><button id="reports_btn"type="button"onclick="toggle_domain(1)">Reports</button><button id="servers_btn"type="button"onclick="toggle_domain(2)">Servers</button></div><input id="search_a"class="search"type="text"name="text"placeholder="Enter: R1, Ctrl+Enter: New Tab, Shift+Enter: Uber"autofocus=""><input id="search_r"class="search"type="text"name="text"placeholder="Enter: First Link,Ctrl+Enter: New Tab,Shift+Enter: Info"></nav></header><main id="agents_window"><aside><div class="filters"><h2>Filters</h2><div class="filter"id="os_btns"><button class="tooltip"type="button"onclick="toggle_os(0)"><div class="icons icons_btn icon_windows_btn"></div><span class="tooltiptext">Windows</span></button><button class="tooltip center"type="button"onclick="toggle_os(1)"><div class="icons icons_btn icon_linux_btn"></div><span class="tooltiptext">Linux</span></button><button class="tooltip"type="button"onclick="toggle_os(2)">?<span class="tooltiptext">Unknown</span></button></div><div class="filter"id="hw_btns"><button class="tooltip"type="button"onclick="toggle_hw(0)"><div class="icons icons_btn icon_hw_btn"></div><span class="tooltiptext">Hardware</span></button><button class="tooltip center"type="button"onclick="toggle_hw(1)"><div class="icons icons_btn icon_vm_btn"></div><span class="tooltiptext">Virtual</span></button><button class="tooltip"type="button"onclick="toggle_hw(2)">?<span class="tooltiptext">Unknown</span></button></div><div class="filter"id="state_btns"><button class="tooltip"type="button"onclick="toggle_state(0)">&#10010;<span class="tooltiptext">Active</span></button><button class="tooltip center"type="button"onclick="toggle_state(1)"><div class="icons icons_btn icon_de_btn"></div><span class="tooltiptext">Deleted</span></button><button class="tooltip"type="button"onclick="toggle_state(2)"><div class="icons icons_btn icon_or_btn"></div><span class="tooltiptext">Orphaned</span></button></div><div class="filter"id="error_btns"><button class="tooltip"type="button"onclick="toggle_error(0)">&#10010;<span class="tooltiptext">No Error</span></button><button class="tooltip center"type="button"onclick="toggle_error(1)"><div class="icons icons_btn icon_error_btn"></div><span class="tooltiptext">Error</span></button><button class="tooltip"type="button"onclick="toggle_error(2)"><div class="icons icons_btn icon_warn_btn"></div><span class="tooltiptext">Warning</span></button></div><div class="filter"id="run_btns"><button class="tooltip"type="button"onclick="toggle_run(0)"><span class="backup"></span><span class="tooltiptext">Backing up</span></button><button class="tooltip center"type="button"onclick="toggle_run(1)"><span class="merge"></span><span class="tooltiptext">Merging</span></button><button class="tooltip"type="button"onclick="toggle_run(2)"><span class="restore"></span><span class="tooltiptext">Restoring</span></button></div></div><div id="sorts"><h2>Sorts</h2><div class="sort"><h3>Size</h3><button type="button"class="center"onclick="sort_toggle(true,3)"> &uarr;</button><button type="button"onclick="sort_toggle(false,3)"> &darr;</button></div><div class="sort"><h3>Used</h3><button type="button"class="center"onclick="sort_toggle(true,'used')"> &uarr;</button><button type="button"onclick="sort_toggle(false,'used')"> &darr;</button></div><div class="sort"><h3>Soft</h3><button type="button"class="center"onclick="sort_toggle(true,4)"> &uarr;</button><button type="button"onclick="sort_toggle(false,4)"> &darr;</button></div><div class="sort"><h3>Hard</h3><button type="button"class="center"onclick="sort_toggle(true,5)"> &uarr;</button><button type="button"onclick="sort_toggle(false,5)"> &darr;</button></div><div class="sort"><h3>A-Z</h3><button type="button"class="center"onclick="sort_toggle(true,'alpha')"> &uarr;</button><button type="button"onclick="sort_toggle(false,'alpha')"> &darr;</button></div></div><div class="servers_list"><h2>Servers</h2></div></aside><div><div class="page_select"></div><section></section></div></main><main id="reports_window"><aside><div class="filters"><h2>Filters</h2></div><div class="servers_list"><h2>Servers</h2></div></aside><div><div class="page_select"></div><section></section></div></main><main id="servers_window"><aside><div class="filters"><h2>Filters</h2></div></aside><h1>THIS IS SERVER PAGE</h1></main></body>
<script>
<?php

$PATH = './ram/';
$files = scandir($PATH);
$array_sorted = array();
foreach ($files as $file) {
    if ($file != '.' || $file != '..') {
        array_push($array_sorted, (int)$file);
    }
}
rsort($array_sorted);

$candidate_file = fopen($PATH. $array_sorted[0], "r") or die("Unable to open file!");

$agents_str = trim(fgets($candidate_file));
$servers_str = trim(fgets($candidate_file));
$end = fgets($candidate_file);
fclose($candidate_file);

if (str_contains($end, "END")) {
    echo "let agents = " . $agents_str . ";\n";
    echo "let servers = " . $servers_str . ";\n";
} else {
    $candidate_file = fopen($PATH . $array_sorted[1], "r") or die("Unable to open file!");
    $agents_str = trim(fgets($candidate_file));
    $servers_str = trim(fgets($candidate_file));
    echo "let agents = " . $agents_str . ";\n";
    echo "let servers = " . $servers_str . ";\n";
    fclose($candidate_file);
}
?>
</script>
<script type="text/javascript" src="fuse.js"></script>
<script type="text/javascript" src="main.js"></script>
<!-- <script type="text/javascript" src="ready.js"></script> -->
<script type="text/javascript" src="lazy.php"></script>
</html>
