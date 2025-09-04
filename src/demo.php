
<?php
/**
 * Demo file for GitHub Actions workflow.
 *
 * PHP version 8.2
 *
 * @category  Demo
 * @package   DemoProject
 * @author    Your Name <you@example.com>
 * @license   MIT License
 * @link      https://github.com/yourname/demo-project
 */

/**
 * Demo function to greet a user.
 *
 * @param string $name Name of the user.
 *
 * @return void
 */
function demoFunction( string $name ): void {
    echo 'Hello ' . $name;
}

// Call the demo function
demoFunction( 'GitHub Actions' );
