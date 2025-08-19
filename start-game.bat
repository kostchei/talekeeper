@echo off
cls
echo =========================================
echo        D^&D 2024 TaleKeeper
echo         Game Startup Script
echo =========================================
echo.

REM Set the script directory as working directory
cd /d "%~dp0"

echo [INFO] Running system diagnostics...

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%v in ('python --version 2^>^&1') do echo [OK] Python %%v installed
)

REM Check Node.js installation
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
) else (
    for /f %%v in ('node --version 2^>^&1') do echo [OK] Node.js %%v installed
)

REM Check Docker availability with detailed testing
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=3" %%v in ('docker --version 2^>^&1') do echo [OK] Docker %%v available
    
    REM Test Docker functionality
    echo [INFO] Testing Docker functionality...
    docker run --rm hello-world >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Docker is working properly
        set DOCKER_AVAILABLE=true
    ) else (
        echo [WARN] Docker installed but not working properly
        echo [INFO] You may need to start Docker Desktop
        set DOCKER_AVAILABLE=partial
    )
) else (
    echo [INFO] Docker not found - will use local development mode
    set DOCKER_AVAILABLE=false
)

REM Test Python dependencies
echo [INFO] Checking Python dependencies...
cd backend 2>nul
if exist requirements.txt (
    python -c "import fastapi, sqlalchemy, pydantic; print('[OK] Core Python dependencies available')" 2>nul
    if %errorlevel% neq 0 (
        echo [INFO] Python dependencies need installation
    )
) else (
    echo [WARN] Backend directory or requirements.txt not found
)
cd .. 2>nul

REM Check frontend dependencies
echo [INFO] Checking frontend dependencies...
if exist frontend\package.json (
    if exist frontend\node_modules (
        echo [OK] Frontend dependencies installed
    ) else (
        echo [INFO] Frontend dependencies need installation
    )
) else (
    echo [WARN] Frontend directory not found
)

echo.
echo Choose startup option:
echo 1. Start Full Stack (Docker with PostgreSQL - Recommended)
echo 2. Start Development Mode (Docker database + local servers)
echo 3. Backend Only (API server only - requires database)
echo 4. Run Full Diagnostics (Advanced testing)
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto docker_start
if "%choice%"=="2" goto local_start
if "%choice%"=="3" goto backend_only
if "%choice%"=="4" goto full_diagnostics
if "%choice%"=="5" goto exit
echo Invalid choice. Defaulting to local development.

:local_start
echo.
echo =========================================
echo   Starting Development Mode
echo =========================================
echo.

REM Start database only in Docker, run servers locally
echo [INFO] Configuring for PostgreSQL database in Docker...
echo [INFO] Creating .env file for development mode...
(
    echo POSTGRES_DB=dnd_game
    echo POSTGRES_USER=dnd_admin
    echo POSTGRES_PASSWORD=secure_password_change_me
    echo DATABASE_URL=postgresql://dnd_admin:secure_password_change_me@localhost:5432/dnd_game
    echo REACT_APP_API_URL=http://localhost:8000
) > .env

REM Start just the database container
echo [INFO] Starting PostgreSQL database container...
docker-compose up -d db
if %errorlevel% neq 0 (
    echo [ERROR] Failed to start database container
    echo Try running: docker-compose down -v
    pause
    exit /b 1
)

REM Wait for database to be ready
echo [INFO] Waiting for database to be ready...
timeout /t 5 /nobreak >nul

REM Install backend dependencies
echo [INFO] Installing backend dependencies...
cd backend
if not exist venv (
    echo [INFO] Creating virtual environment...
    python -m venv venv
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Installing Python packages...
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install backend dependencies
    pause
    exit /b 1
)

echo [OK] Backend dependencies installed

REM Test database connection and setup
echo [INFO] Setting up database tables...
python -c "from database import init_db, test_connection; print('[OK] Database connected') if test_connection() else exit(1); init_db(); print('[OK] Database initialized')"
if %errorlevel% neq 0 (
    echo [ERROR] Database setup failed - is PostgreSQL container running?
    echo [INFO] You can check with: docker-compose logs db
    pause
    exit /b 1
)

REM Install frontend dependencies
echo [INFO] Installing frontend dependencies...
cd ..\frontend
if not exist node_modules (
    echo [INFO] Running npm install...
    npm install >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install frontend dependencies
        pause
        exit /b 1
    )
)

echo [OK] Frontend dependencies installed

REM Start backend in background
echo [INFO] Starting backend server...
cd ..\backend
start "TaleKeeper Backend" cmd /k "call venv\Scripts\activate.bat && python main.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Backend is starting in background window
echo [INFO] Backend server is starting in separate window...
timeout /t 3 /nobreak >nul
echo [INFO] Backend should be available at http://localhost:8000

REM Start frontend in separate window
echo [INFO] Starting frontend...
cd ..\frontend
start "TaleKeeper Frontend" cmd /k "npm start"

echo.
echo =========================================
echo   Development Mode Started!
echo =========================================
echo.
echo Database: PostgreSQL in Docker (port 5432)
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs  
echo Frontend: http://localhost:3000
echo.
echo Both servers are starting in separate windows...
echo The game will open in your browser shortly...
echo.
echo To stop:
echo - Press Ctrl+C in server windows to stop backend/frontend
echo - Run: docker-compose stop db  (to stop database)
echo - Or: docker-compose down  (to stop and remove containers)

goto end

:docker_start
echo.
echo =========================================
echo      Starting with Docker
echo =========================================
echo.

if "%DOCKER_AVAILABLE%"=="false" (
    echo [ERROR] Docker is not available
    echo Please install Docker Desktop from https://docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Ensure we're using PostgreSQL in .env for Docker
echo [INFO] Configuring for PostgreSQL database...
echo [INFO] Creating .env file for Docker mode...
(
    echo POSTGRES_DB=dnd_game
    echo POSTGRES_USER=dnd_admin
    echo POSTGRES_PASSWORD=secure_password_change_me
    echo DATABASE_URL=postgresql://dnd_admin:secure_password_change_me@db:5432/dnd_game
    echo REACT_APP_API_URL=http://localhost:8000
) > .env

echo [INFO] Starting Docker containers...
echo This may take a few minutes on first run...
echo.

docker-compose up --build
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Docker startup failed!
    echo.
    echo Try running: fix-docker.bat to clean up Docker issues
    echo Or select option 2 for Local Development mode
    echo.
    pause
)

goto end

:backend_only
echo.
echo =========================================
echo     Starting Backend Only
echo =========================================
echo.

REM Use PostgreSQL - ensure database is running
echo [INFO] Configuring for PostgreSQL database...
if not exist .env (
    (
        echo POSTGRES_DB=dnd_game
        echo POSTGRES_USER=dnd_admin
        echo POSTGRES_PASSWORD=secure_password_change_me
        echo DATABASE_URL=postgresql://dnd_admin:secure_password_change_me@localhost:5432/dnd_game
        echo REACT_APP_API_URL=http://localhost:8000
    ) > .env
)

echo [INFO] Checking if database is running...
docker-compose ps db 2>nul | findstr "Up" >nul
if %errorlevel% neq 0 (
    echo [WARN] Database container not running. Starting database...
    docker-compose up -d db
    echo [INFO] Waiting for database...
    timeout /t 5 /nobreak >nul
)

cd backend
if not exist venv (
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1

echo [INFO] Starting backend server...
echo.
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo Database: PostgreSQL in Docker (port 5432)
echo.
echo Press Ctrl+C to stop the backend server
echo To stop database: docker-compose stop db
echo.

python main.py

goto end

:full_diagnostics
echo.
echo =========================================
echo      Full System Diagnostics
echo =========================================
echo.

REM Detailed system information
echo [INFO] System Information:
echo OS: %OS%
echo Processor: %PROCESSOR_ARCHITECTURE%
echo User: %USERNAME%
echo.

REM Enhanced Python testing
echo [TEST] Python Environment:
python --version
python -c "import sys; print(f'Python path: {sys.executable}')"
python -c "import platform; print(f'Platform: {platform.platform()}')"
echo.

REM Enhanced Node.js testing
echo [TEST] Node.js Environment:
node --version
npm --version
echo Node.js path: 
where node
echo.

REM Database testing
echo [TEST] Database Setup:
cd backend
if exist requirements.txt (
    if not exist venv (
        echo [INFO] Creating virtual environment for testing...
        python -m venv venv
    )
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
    
    echo [INFO] Installing/checking dependencies...
    pip install -r requirements.txt >nul 2>&1
    
    echo [INFO] Testing database connection...
    python -c "from database import test_connection, init_db; print('[PASS] Database connection successful') if test_connection() else print('[FAIL] Database connection failed'); init_db(); print('[PASS] Database tables created/verified')" 2>nul
    
    echo [INFO] Testing API endpoints...
    python -c "from main import app; from fastapi.testclient import TestClient; client = TestClient(app); r1 = client.get('/health'); r2 = client.get('/api/items/equipment'); print('[PASS] Health endpoint working' if r1.status_code == 200 else '[FAIL] Health endpoint failed'); print('[PASS] Items API working' if r2.status_code == 200 else '[FAIL] Items API failed'); print(f'[INFO] Total API routes: {len([r for r in app.routes if hasattr(r, \"path\")])}')" 2>nul
) else (
    echo [FAIL] requirements.txt not found
)
cd ..

echo.
echo [TEST] Frontend Environment:
cd frontend
if exist package.json (
    echo [INFO] Frontend configuration found
    if exist node_modules (
        echo [PASS] Dependencies installed
        echo [INFO] Checking React setup...
        npm ls react react-dom --depth=0 2>nul
    ) else (
        echo [INFO] Installing frontend dependencies...
        npm install >nul 2>&1
        if %errorlevel% equ 0 (
            echo [PASS] Frontend dependencies installed successfully
        ) else (
            echo [FAIL] Frontend installation failed
        )
    )
) else (
    echo [FAIL] package.json not found
)
cd ..

echo.
echo [TEST] Docker Environment:
if "%DOCKER_AVAILABLE%"=="true" (
    echo [INFO] Testing Docker Compose configuration...
    docker-compose config >nul 2>&1
    if %errorlevel% equ 0 (
        echo [PASS] Docker Compose configuration valid
        
        echo [INFO] Testing container build capability...
        docker-compose build --no-cache backend >nul 2>&1
        if %errorlevel% equ 0 (
            echo [PASS] Backend container builds successfully
        ) else (
            echo [WARN] Backend container build issues
        )
    ) else (
        echo [FAIL] Docker Compose configuration has errors
    )
) else (
    echo [INFO] Docker not available - skipping Docker tests
)

echo.
echo [TEST] Port Availability:
netstat -an | findstr ":3000" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARN] Port 3000 is in use (frontend port)
) else (
    echo [PASS] Port 3000 available
)

netstat -an | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARN] Port 8000 is in use (backend port)
) else (
    echo [PASS] Port 8000 available
)

netstat -an | findstr ":5432" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARN] Port 5432 is in use (PostgreSQL port)
) else (
    echo [PASS] Port 5432 available
)

echo.
echo [TEST] File System:
echo [INFO] Checking project structure...
if exist backend\main.py (
    echo [PASS] Backend main.py found
) else (
    echo [FAIL] Backend main.py missing
)

if exist frontend\src\App.js (
    echo [PASS] Frontend App.js found
) else (
    echo [FAIL] Frontend App.js missing
)

if exist database\init.sql (
    echo [PASS] Database schema found
) else (
    echo [FAIL] Database schema missing
)

if exist .env (
    echo [PASS] Environment file found
    echo [INFO] Current configuration:
    type .env | findstr "DATABASE_URL"
) else (
    echo [WARN] Environment file missing
)

echo.
echo =========================================
echo     Diagnostic Test Complete
echo =========================================
echo.
echo All tests completed! Check results above for any issues.
echo.
pause
goto end

:exit
echo Goodbye!
exit /b 0

:end
echo.
echo =========================================
echo      TaleKeeper Shutdown
echo =========================================
echo.
pause