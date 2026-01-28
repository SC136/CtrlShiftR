# 🚀 ATHARVA Production Startup Script
# Verifies everything is ready and starts all services

$ErrorActionPreference = "Stop"

Write-Host "="*70 -ForegroundColor Green
Write-Host "🌾 ATHARVA FARMER ASSISTANT - PRODUCTION STARTUP" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Green

# Environment setup
$env:KMP_DUPLICATE_LIB_OK = "TRUE"

# Helper function for colored output
function Write-Step {
    param($message)
    Write-Host "`n[STEP] $message" -ForegroundColor Cyan
}

function Write-Success {
    param($message)
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Error {
    param($message)
    Write-Host "❌ $message" -ForegroundColor Red
}

function Write-Warning {
    param($message)
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

# Check Prerequisites
Write-Step "Checking Prerequisites..."

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python not found! Please install Python 3.8+"
    exit 1
}
Write-Success "Python installed"

# Check if model exists
Write-Step "Checking trained model..."
if (-not (Test-Path "image_classifier\output\best_model.pth")) {
    Write-Error "Trained model not found!"
    Write-Host "`nPlease train the model first:" -ForegroundColor Yellow
    Write-Host "  cd image_classifier" -ForegroundColor White
    Write-Host "  python train.py --dataset <DATASET_PATH> --epochs 30 --batch-size 16" -ForegroundColor White
    exit 1
}
Write-Success "Trained model found"

# Check class mapping
if (-not (Test-Path "image_classifier\output\class_map.json")) {
    Write-Error "Class mapping not found!"
    exit 1
}
Write-Success "Class mapping found"

# Check LLM model
Write-Step "Checking LLM model..."
if (-not (Test-Path "models\qwen2.5-1.5b-instruct-q4_k_m.gguf")) {
    Write-Error "LLM model file not found!"
    Write-Host "Expected: models\qwen2.5-1.5b-instruct-q4_k_m.gguf" -ForegroundColor Yellow
    exit 1
}
Write-Success "LLM model found"

# Check llama-cli
if (-not (Test-Path "reasoning_layer\llama\llama-cli.exe")) {
    Write-Error "llama-cli.exe not found!"
    Write-Host "Expected: reasoning_layer\llama\llama-cli.exe" -ForegroundColor Yellow
    exit 1
}
Write-Success "llama-cli.exe found"

# Get network information
Write-Step "Getting network configuration..."
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*"} | Select-Object -First 1).IPAddress

if (-not $localIP) {
    $localIP = "localhost"
    Write-Warning "Could not detect local network IP. Using localhost."
} else {
    Write-Success "Local network IP: $localIP"
}

Write-Host "`n📱 Mobile App Configuration:" -ForegroundColor Yellow
Write-Host "   To connect from mobile device, update:" -ForegroundColor White
Write-Host "   File: atharva_UI\services\api.ts" -ForegroundColor White
Write-Host "   Change: const BACKEND_HOST = '$localIP'" -ForegroundColor Green
Write-Host "`n   Note: Ensure mobile device is on the SAME WiFi network" -ForegroundColor Yellow

# Check if ports are free
Write-Step "Checking port availability..."
$port8000 = netstat -ano | findstr ":8000" | findstr "LISTENING"
$port8001 = netstat -ano | findstr ":8001" | findstr "LISTENING"

if ($port8000) {
    Write-Warning "Port 8000 is already in use. Stopping existing process..."
    $pid = ($port8000 -split '\s+')[-1]
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

if ($port8001) {
    Write-Warning "Port 8001 is already in use. Stopping existing process..."
    $pid = ($port8001 -split '\s+')[-1]
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

Write-Success "Ports 8000 and 8001 are available"

# Install dependencies
Write-Step "Installing/Updating dependencies..."
Write-Host "   Image Classifier..." -ForegroundColor Yellow
Set-Location image_classifier
pip install -q -r requirements.txt 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install image classifier dependencies"
    Set-Location ..
    exit 1
}

Write-Host "   Reasoning Layer..." -ForegroundColor Yellow
Set-Location ..\reasoning_layer
pip install -q -r requirements.txt 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to install reasoning layer dependencies"
    Set-Location ..
    exit 1
}

Set-Location ..
Write-Success "Dependencies installed"

# Start services
Write-Host "`n"*70 -ForegroundColor Green
Write-Host "🚀 STARTING BACKEND SERVICES" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Green

Write-Host "`n📊 Service URLs:" -ForegroundColor Cyan
Write-Host "   Image Classifier API: http://localhost:8000" -ForegroundColor White
Write-Host "   Image Classifier Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Reasoning Service API: http://localhost:8001" -ForegroundColor White
Write-Host "   Reasoning Service Docs: http://localhost:8001/docs" -ForegroundColor White

Write-Host "`n📱 From Mobile Device (on same WiFi):" -ForegroundColor Cyan
Write-Host "   Image Classifier: http://${localIP}:8000" -ForegroundColor White
Write-Host "   Reasoning Service: http://${localIP}:8001" -ForegroundColor White

Write-Host "`n⚠️  Services will start in separate windows. Keep them running!" -ForegroundColor Yellow
Write-Host "Press CTRL+C in each window to stop services." -ForegroundColor Yellow
Write-Host "`nStarting in 3 seconds..." -ForegroundColor White
Start-Sleep -Seconds 3

# Start Image Classifier
Write-Host "`n🔵 Starting Image Classifier..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\image_classifier'; python -m uvicorn api:app --host 0.0.0.0 --port 8000" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start Reasoning Layer
Write-Host "🟢 Starting Reasoning Service..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\reasoning_layer'; python -m uvicorn main:app --host 0.0.0.0 --port 8001" -WindowStyle Normal

Start-Sleep -Seconds 5

# Verify services are running
Write-Step "Verifying services..."

try {
    $healthImage = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    if ($healthImage.model_loaded) {
        Write-Success "Image Classifier is running and model loaded ($($healthImage.num_classes) classes)"
    } else {
        Write-Warning "Image Classifier is running but model not loaded"
    }
} catch {
    Write-Error "Image Classifier not responding. Check the service window for errors."
}

try {
    $healthReason = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5
    Write-Success "Reasoning Service is running"
} catch {
    Write-Error "Reasoning Service not responding. Check the service window for errors."
}

# Final instructions
Write-Host "`n"*70 -ForegroundColor Green
Write-Host "✅ BACKEND SERVICES RUNNING" -ForegroundColor Green
Write-Host "="*70 -ForegroundColor Green

Write-Host "`n📱 To start the mobile app:" -ForegroundColor Cyan
Write-Host "   1. Open a new terminal" -ForegroundColor White
Write-Host "   2. cd atharva_UI" -ForegroundColor White
Write-Host "   3. npm install (first time only)" -ForegroundColor White
Write-Host "   4. npx expo start" -ForegroundColor White
Write-Host "   5. Scan QR code with Expo Go app" -ForegroundColor White

Write-Host "`n🧪 To test the system:" -ForegroundColor Cyan
Write-Host "   python test_integration_full.py" -ForegroundColor White

Write-Host "`n⚠️  Keep this window and service windows open!" -ForegroundColor Yellow
Write-Host "Press any key to exit (services will keep running)..." -ForegroundColor White
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
