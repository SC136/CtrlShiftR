# ========================================
# 🌾 FARMER ASSISTANT - ONE-COMMAND STARTUP
# ========================================
# This script starts all three services:
# 1. Image Classifier API (Port 8000)
# 2. Reasoning Layer API (Port 8002)  
# 3. Expo Development Server (Port 8081)
# ========================================

Write-Host ('=' * 70) -ForegroundColor Green
Write-Host '🌾 FARMER ASSISTANT - STARTING ALL SERVICES' -ForegroundColor Green
Write-Host ('=' * 70) -ForegroundColor Green

# Configuration
$PROJECT_ROOT = $PSScriptRoot
$VENV_PYTHON = "$PROJECT_ROOT\.venv\Scripts\python.exe"
$VENV_UVICORN = "$PROJECT_ROOT\.venv\Scripts\uvicorn.exe"

# Check if virtual environment exists
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "❌ Virtual environment not found at .venv" -ForegroundColor Red
    Write-Host "   Please run: python -m venv .venv" -ForegroundColor Yellow
    Write-Host "   Then install dependencies: .venv\Scripts\pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Check if Node.js is installed
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "❌ Node.js not found! Please install Node.js" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Prerequisites checked" -ForegroundColor Green

# Kill existing processes on our ports
Write-Host "`n🧹 Cleaning up existing processes..." -ForegroundColor Cyan
$ports = @(8000, 8002, 8081)
foreach ($port in $ports) {
    $connections = netstat -ano | Select-String ":$port.*LISTENING"
    if ($connections) {
        $connections | ForEach-Object {
            if ($_ -match '\s+(\d+)$') {
                $pid = $matches[1]
                try {
                    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                    Write-Host "   Killed process $pid on port $port" -ForegroundColor Yellow
                } catch {
                    Write-Host "   Could not kill process $pid" -ForegroundColor DarkYellow
                }
            }
        }
    }
}
Start-Sleep -Seconds 2

# Function to start a service in a new window
function Start-Service {
    param(
        [string]$Name,
        [string]$Command,
        [string]$WorkingDirectory
    )
    
    Write-Host "🚀 Starting $Name..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkingDirectory'; Write-Host '🌾 $Name' -ForegroundColor Green; $Command" -WindowStyle Normal
    Start-Sleep -Seconds 3
}

# Start Image Classifier API
Write-Host "`n📦 Starting Backend Services..." -ForegroundColor Cyan
Start-Service -Name "Image Classifier API (Port 8000)" `
              -Command "`$env:KMP_DUPLICATE_LIB_OK='TRUE'; & '$VENV_PYTHON' image_classifier\api.py" `
              -WorkingDirectory $PROJECT_ROOT

# Start Reasoning Layer API
Start-Service -Name "Reasoning Layer API (Port 8002)" `
              -Command "& '$VENV_UVICORN' reasoning_layer.main:app --host 0.0.0.0 --port 8002" `
              -WorkingDirectory $PROJECT_ROOT

# Start Expo Development Server
Write-Host "`n📱 Starting Expo Development Server..." -ForegroundColor Cyan
Start-Service -Name "Expo Development Server (Port 8081)" `
              -Command "npx expo start" `
              -WorkingDirectory "$PROJECT_ROOT\atharva_UI"

# Wait and verify services
Write-Host "`n⏳ Waiting for services to start..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

Write-Host "`n🔍 Verifying services..." -ForegroundColor Cyan

# Check ports
$allRunning = $true
$serviceInfo = @(
    @{Name="Image Classifier API"; Port=8000; URL="http://localhost:8000/health"},
    @{Name="Reasoning Layer API"; Port=8002; URL="http://localhost:8002/docs"},
    @{Name="Expo Dev Server"; Port=8081; URL="http://localhost:8081"}
)

foreach ($service in $serviceInfo) {
    $listening = netstat -ano | Select-String ":$($service.Port).*LISTENING"
    if ($listening) {
        Write-Host "   ✅ $($service.Name) - Running on port $($service.Port)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $($service.Name) - NOT running on port $($service.Port)" -ForegroundColor Red
        $allRunning = $false
    }
}

# Display summary
Write-Host "`n" + ("=" * 70) -ForegroundColor Green
if ($allRunning) {
    Write-Host "✅ ALL SERVICES STARTED SUCCESSFULLY!" -ForegroundColor Green
} else {
    Write-Host "⚠️  SOME SERVICES FAILED TO START" -ForegroundColor Yellow
}
Write-Host ("=" * 70) -ForegroundColor Green

Write-Host "`n📋 Service URLs:" -ForegroundColor Cyan
Write-Host "   • Image Classifier API: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   • Image Classifier Health: http://localhost:8000/health" -ForegroundColor White
Write-Host "   • Reasoning Layer API: http://localhost:8002/docs" -ForegroundColor White
Write-Host "   • Expo Dev Server: http://localhost:8081" -ForegroundColor White

Write-Host "`n📱 Mobile App:" -ForegroundColor Cyan
Write-Host "   • Scan the QR code in the Expo window" -ForegroundColor White
Write-Host "   • Or press 'a' for Android, 'i' for iOS, 'w' for web" -ForegroundColor White

Write-Host "`n⚙️  Backend Configuration:" -ForegroundColor Cyan
Write-Host "   • Make sure atharva_UI/services/api.ts has your IP address" -ForegroundColor White
Write-Host "   • Current setting: BACKEND_HOST = '192.168.137.1'" -ForegroundColor White
Write-Host "   • Find your IP: ipconfig (look for IPv4)" -ForegroundColor White

Write-Host "`n🔴 To stop all services:" -ForegroundColor Cyan
Write-Host "   • Close all PowerShell windows" -ForegroundColor White
Write-Host "   • Or run: .\stop_all.ps1" -ForegroundColor White

Write-Host (('=' * 70)) -ForegroundColor Green
Write-Host 'Press any key to exit this window...' -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
