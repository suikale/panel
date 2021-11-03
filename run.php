<?php
    $id = $_POST['input'];
    shell_exec("./postparser.py \"" . $id . "\"");
    header('Location: http://192.168.1.135/panel/index.html?success=true');
?>
