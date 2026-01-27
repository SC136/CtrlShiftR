# Quick Start Guide - No CMake Required!
# Use Python bindings instead of building llama.cpp

Write-Host "===== QUICK START - PYTHON BINDINGS =====" -ForegroundColor Green
Write-Host ""

Write-Host "[1/3] Installing llama-cpp-python..." -ForegroundColor Cyan
.\.venv\Scripts\python.exe -m pip install llama-cpp-python requests

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install llama-cpp-python" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Installation successful!" -ForegroundColor Green
Write-Host ""

Write-Host "[2/3] Creating models directory..." -ForegroundColor Cyan
if (-not (Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
    Write-Host "✓ Created models/" -ForegroundColor Green
}
else {
    Write-Host "✓ models/ already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "[3/3] Checking for model file..." -ForegroundColor Cyan

$modelFile = "models\qwen2.5-1.5b-instruct-q4_k_m.gguf"
if (Test-Path $modelFile) {
    Write-Host "✓ Model file found!" -ForegroundColor Green
    $modelSize = (Get-Item $modelFile).Length / 1MB
    Write-Host "  Size: $([math]::Round($modelSize, 2)) MB" -ForegroundColor White
}
else {
    Write-Host "⚠ Model file NOT found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "DOWNLOAD THE MODEL:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF" -ForegroundColor Cyan
    Write-Host "  2. Download: qwen2.5-1.5b-instruct-q4_k_m.gguf (~1GB)" -ForegroundColor Cyan
    Write-Host "  3. Place in: models\" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "===== SETUP COMPLETE =====" -ForegroundColor Green
Write-Host ""
Write-Host "TO START THE SERVER:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\python.exe -m uvicorn main_python:app --reload" -ForegroundColor Cyan
Write-Host ""
Write-Host "TO TEST:" -ForegroundColor Yellow
Write-Host "  .\.venv\Scripts\python.exe test_api.py" -ForegroundColor Cyan
Write-Host ""
