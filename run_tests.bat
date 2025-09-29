@echo off
REM TaleKeeper Regression Test Runner (Windows)
REM Usage: run_tests.bat [quick|full|verbose]

set MODE=%1
if "%MODE%"=="" set MODE=quick

echo Running TaleKeeper regression tests in %MODE% mode...
echo.

if "%MODE%"=="verbose" (
    python tests/run_regression_tests.py --%MODE% --verbose
) else (
    python tests/run_regression_tests.py --%MODE%
)

pause