
<?php

// Intentionally bad formatting and deprecated usage for testing

function demoFunction($name) {
  echo "Hello ".$name;
}

demoFunction("GitHub Actions");

$unusedVar = 123; // Unused variable to trigger PHPStan warning
