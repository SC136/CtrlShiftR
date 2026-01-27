# 🌾 FARMER ASSISTANT - STARTUP SCRIPT
# Starts both classification and reasoning APIs

Write-Host "=" -NoNewline -ForegroundColor Green
Write-Host ("=" * 69) -ForegroundColor Green
Write-Host "🌾 FARMER ASSISTANT - STARTING SERVICES" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Cyan
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python not found! Please install Python 3.8+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python found: $($python.Version)" -ForegroundColor Green

# Create output directory for models
Write-Host "`nCreating directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path "image_classifier\output" | Out-Null
New-Item -ItemType Directory -Force -Path "reasoning_layer\models" | Out-Null
Write-Host "✅ Directories created" -ForegroundColor Green

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Cyan
Write-Host "  Image Classifier..." -ForegroundColor Yellow
Set-Location image_classifier
pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install image classifier dependencies" -ForegroundColor Red
    exit 1
}

Write-Host "  Reasoning Layer..." -ForegroundColor Yellow
Set-Location ..\reasoning_layer
pip install -q -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install reasoning layer dependencies" -ForegroundColor Red
    exit 1
}
Set-Location ..

Write-Host "✅ Dependencies installed" -ForegroundColor Green

# Check if model exists
Write-Host "`nChecking for trained model..." -ForegroundColor Cyan
if (Test-Path "image_classifier\output\best_model.pth") {
    Write-Host "✅ Trained model found" -ForegroundColor Green
    $hasModel = $true
} else {
    Write-Host "⚠️  No trained model found" -ForegroundColor Yellow
    Write-Host "   The image classifier will start but won't work until you train a model." -ForegroundColor Yellow
    Write-Host "   To train: cd image_classifier && python train.py --dataset /path/to/dataset" -ForegroundColor Yellow
    $hasModel = $false
}

# Start services
Write-Host "`n" + ("=" * 70) -ForegroundColor Green
Write-Host "🚀 STARTING SERVICES" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green

Write-Host "`nStarting Image Classification API (port 8000)..." -ForegroundColor Cyan
$classifierJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\image_classifier
    python api.py --host 0.0.0.0 --port 8000
}
Start-Sleep -Seconds 3
Write-Host "✅ Image Classifier started (Job ID: $($classifierJob.Id))" -ForegroundColor Green

Write-Host "`nStarting LLM Reasoning API (port 8001)..." -ForegroundColor Cyan
$reasoningJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD\reasoning_layer
    python main_demo.py
}
Start-Sleep -Seconds 3
Write-Host "✅ Reasoning Layer started (Job ID: $($reasoningJob.Id))" -ForegroundColor Green

# Wait for services to be ready
Write-Host "`nWaiting for services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Test endpoints
Write-Host "`nTesting endpoints..." -ForegroundColor Cyan

try {
    $classifierHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "  ✅ Classification API: " -NoNewline -ForegroundColor Green
    Write-Host "http://localhost:8000" -ForegroundColor Cyan
} catch {
    Write-Host "  ⚠️  Classification API not responding yet" -ForegroundColor Yellow
}

try {
    $reasoningHealth = Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get -TimeoutSec 5
    Write-Host "  ✅ Reasoning API: " -NoNewline -ForegroundColor Green
    Write-Host "http://localhost:8001" -ForegroundColor Cyan
} catch {
    Write-Host "  ⚠️  Reasoning API not responding yet" -ForegroundColor Yellow
}

# Summary
Write-Host "`n" + ("=" * 70) -ForegroundColor Green
Write-Host "✅ SERVICES RUNNING" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green
Write-Host "`nAPI Documentation:"
Write-Host "  Classification: " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:8000/docs"
Write-Host "  Reasoning:      " -NoNewline -ForegroundColor Cyan
Write-Host "http://localhost:8001/docs"

Write-Host "`nTest the pipeline:"
Write-Host "  python test_integration.py --health" -ForegroundColor Yellow
Write-Host "  python test_integration.py --image path/to/test.jpg" -ForegroundColor Yellow

Write-Host "`nPress Ctrl+C to stop all services" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Green

# Wait for user interrupt
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host "`n`nStopping services..." -ForegroundColor Yellow
    Stop-Job $classifierJob, $reasoningJob
    Remove-Job $classifierJob, $reasoningJob
    Write-Host "✅ Services stopped" -ForegroundColor Green
}
