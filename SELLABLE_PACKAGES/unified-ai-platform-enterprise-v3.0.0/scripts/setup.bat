@echo off
echo Setting up Unified AI Platform...

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo Docker is required but not installed. Please install Docker Desktop.
    pause
    exit /b 1
)

REM Create environment files
if not exist "bridge-api\.env" (
    copy "bridge-api\.env.example" "bridge-api\.env"
    echo Created bridge-api\.env - please configure your settings
)

if not exist "evolution-framework\.env" (
    echo BRIDGE_API_URL=http://localhost:3001 > "evolution-framework\.env"
    echo Created evolution-framework\.env
)

REM Start services
echo Starting services with Docker Compose...
docker-compose -f deployment\docker-compose.prod.yml up -d

echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo Unified AI Platform is running!
echo Bridge API: http://localhost:3001
echo Evolution Framework: http://localhost:5000
echo Health Status: http://localhost:3001/health

pause
