<?php

declare(strict_types=1);

use Rector\Config\RectorConfig;
use Rector\Set\ValueObject\SetList;

return static function (RectorConfig $rectorConfig): void {
    // Use a predefined set of rules
    $rectorConfig->sets([
        SetList::CODE_QUALITY,
        SetList::DEAD_CODE,
        SetList::PHP_80, // Or whichever PHP version you target
    ]);

    // Optional: paths to analyze
    $rectorConfig->paths([
        __DIR__ . '/src',
    ]);
};
