<?php
// Simple redirect script
// Usage: redirect.php?file=/path/to/file
if (isset($_GET['file'])) {
    header('Location: file://' . $_GET['file']);
    exit();
}
echo "Usage: ?file=/path/to/file";
?>
