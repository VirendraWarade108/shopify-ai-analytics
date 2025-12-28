# Quick Start Script for Shopify Analytics AI
# Save as: start-services.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Shopify Analytics AI - Quick Start   " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "rails_api") -or -not (Test-Path "ai_service")) {
    Write-Host "ERROR: Please run this script from the project root directory!" -ForegroundColor Red
    Write-Host "Expected structure:" -ForegroundColor Yellow
    Write-Host "  shopify-ai-analytics/" -ForegroundColor Yellow
    Write-Host "    ├── rails_api/" -ForegroundColor Yellow
    Write-Host "    └── ai_service/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Current directory: $PWD" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Project directory found" -ForegroundColor Green
Write-Host ""

# Check Ruby
Write-Host "Checking Ruby..." -ForegroundColor Yellow
try {
    $rubyVersion = ruby -v
    Write-Host "✓ Ruby installed: $rubyVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Ruby not found! Please install Ruby 3.3.10 from:" -ForegroundColor Red
    Write-Host "  https://rubyinstaller.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Python installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.11+ from:" -ForegroundColor Red
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Starting Services...                  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Rails API
Write-Host "Starting Rails API on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PWD\rails_api'; " +
    "Write-Host 'Rails API Server' -ForegroundColor Cyan; " +
    "Write-Host '==================' -ForegroundColor Cyan; " +
    "Write-Host ''; " +
    "bundle exec rails s"
)

# Wait for Rails to initialize
Write-Host "Waiting for Rails to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Python AI Service
Write-Host "Starting Python AI Service on port 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$PWD\ai_service'; " +
    "Write-Host 'Python AI Service' -ForegroundColor Cyan; " +
    "Write-Host '==================' -ForegroundColor Cyan; " +
    "Write-Host ''; " +
    ".\venv\Scripts\Activate.ps1; " +
    "uvicorn main:app --reload --port 8000"
)

# Wait for services to start
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Services Started!                     " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Rails API:      http://localhost:3000" -ForegroundColor Yellow
Write-Host "Python AI:      http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "To test the services, run in a new terminal:" -ForegroundColor Cyan
Write-Host "  curl http://localhost:3000/health" -ForegroundColor White
Write-Host "  curl http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "To stop services: Close the PowerShell windows or press Ctrl+C" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation: See docs/COMPLETE_SETUP_GUIDE.md" -ForegroundColor Yellow
Write-Host ""