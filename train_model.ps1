# ========================================
# 🌾 FARMER ASSISTANT - TRAIN MODEL
# ========================================
# Train the image classifier model
# ========================================

Write-Host ('=' * 70) -ForegroundColor Green
Write-Host '🌾 FARMER ASSISTANT - MODEL TRAINING' -ForegroundColor Green
Write-Host ('=' * 70) -ForegroundColor Green

$PROJECT_ROOT = $PSScriptRoot
$VENV_PYTHON = "$PROJECT_ROOT\.venv\Scripts\python.exe"

# Check virtual environment
if (-not (Test-Path $VENV_PYTHON)) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    exit 1
}

# Training parameters
$DATASET_PATH = "C:\Users\advdi\.cache\kagglehub\datasets\emmarex\plantdisease\versions\1\PlantVillage\PlantVillage"
$EPOCHS = 100
$BATCH_SIZE = 32
$LEARNING_RATE = 0.001
$OUTPUT_DIR = "output"

# Check if dataset exists
if (-not (Test-Path $DATASET_PATH)) {
    Write-Host "❌ Dataset not found at: $DATASET_PATH" -ForegroundColor Red
    Write-Host "   The script will attempt to download it automatically..." -ForegroundColor Yellow
}

Write-Host "`n📋 Training Configuration:" -ForegroundColor Cyan
Write-Host "   • Epochs: $EPOCHS" -ForegroundColor White
Write-Host "   • Batch Size: $BATCH_SIZE" -ForegroundColor White
Write-Host "   • Learning Rate: $LEARNING_RATE" -ForegroundColor White
Write-Host "   • Output Directory: $OUTPUT_DIR" -ForegroundColor White
Write-Host "   • Dataset: $DATASET_PATH" -ForegroundColor White

Write-Host "`n⚠️  Training will take several hours!" -ForegroundColor Yellow
Write-Host "   • 100 epochs on CPU: ~6-10 hours" -ForegroundColor White
Write-Host "   • You can reduce epochs for faster testing (e.g., --epochs 10)" -ForegroundColor White

$response = Read-Host "`nDo you want to continue? (y/n)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "Training cancelled." -ForegroundColor Yellow
    exit 0
}

Write-Host "`n🚀 Starting training..." -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green

# Set environment variable to avoid OpenMP issues
$env:KMP_DUPLICATE_LIB_OK = "TRUE"

# Change to image_classifier directory and run training
Set-Location "$PROJECT_ROOT\image_classifier"

& $VENV_PYTHON train.py `
    --dataset $DATASET_PATH `
    --epochs $EPOCHS `
    --batch-size $BATCH_SIZE `
    --lr $LEARNING_RATE `
    --output $OUTPUT_DIR

$exitCode = $LASTEXITCODE

Set-Location $PROJECT_ROOT

if ($exitCode -eq 0) {
    Write-Host "`n" + ("=" * 70) -ForegroundColor Green
    Write-Host "✅ TRAINING COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Green
    Write-Host "`n📦 Model files saved to: image_classifier\$OUTPUT_DIR" -ForegroundColor Cyan
    Write-Host "   • best_model.pth - Trained model weights" -ForegroundColor White
    Write-Host "   • class_map.json - Class name mappings" -ForegroundColor White
    Write-Host "   • training_history.json - Training metrics" -ForegroundColor White
    Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Start the services: .\start_all.ps1" -ForegroundColor White
    Write-Host "   2. Test the model with the mobile app" -ForegroundColor White
} else {
    Write-Host "`n" + ("=" * 70) -ForegroundColor Red
    Write-Host "❌ TRAINING FAILED!" -ForegroundColor Red
    Write-Host "=" * 70 -ForegroundColor Red
    Write-Host "`nCheck the error messages above for details." -ForegroundColor Yellow
}

Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
