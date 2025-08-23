@echo off
REM Build TaleKeeper Desktop Windows Executable
REM Run this script to build the application locally

echo Building TaleKeeper Desktop v0.01...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again
    pause
    exit /b 1
)

REM Install/upgrade dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Clean previous build
echo Cleaning previous build...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Create directories
mkdir dist 2>nul
mkdir build 2>nul

REM Build executable
echo.
echo Building executable with PyInstaller...
echo This may take a few minutes...
echo.

pyinstaller build.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for details
    pause
    exit /b 1
)

REM Check if executable was created
if not exist "dist\TaleKeeper.exe" (
    echo ERROR: Executable was not created!
    pause
    exit /b 1
)

REM Get file size
for %%A in (dist\TaleKeeper.exe) do set size=%%~zA
set /a sizeMB=%size%/1048576

echo.
echo ================================
echo BUILD SUCCESSFUL!
echo ================================
echo.
echo Executable: dist\TaleKeeper.exe
echo Size: %sizeMB% MB
echo.
echo You can now run dist\TaleKeeper.exe
echo.

REM Ask if user wants to test the executable
set /p test="Test the executable now? (y/n): "
if /i "%test%"=="y" (
    echo Starting TaleKeeper...
    start "" "dist\TaleKeeper.exe"
)

pause