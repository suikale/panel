<?php
    $in = $_POST['input'];
    shell_exec("./postparser.py \"" . $in . "\"");
?>
