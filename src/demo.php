
<?php
/**
 * Demo file for GitHub Actions workflow.
 *
 * @package DemoProject
 */

/**
 * Demo function to greet a user.
 *
 * @param string $name Name of the user.
 *
 * @return void
 */
function demoFunction( string $name ): void
{
    echo 'Hello ' . $name;
}

// Call the demo function
demoFunction( 'GitHub Actions' );

// Remove unused variable to pass PHPStan as well
// $unusedVar = 123; // unused
