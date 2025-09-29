#!/bin/bash
# TaleKeeper Regression Test Runner (Unix/Linux)
# Usage: ./run_tests.sh [quick|full|verbose]

MODE=${1:-quick}

echo "Running TaleKeeper regression tests in $MODE mode..."
echo

if [ "$MODE" = "verbose" ]; then
    python tests/run_regression_tests.py --$MODE --verbose
else
    python tests/run_regression_tests.py --$MODE
fi