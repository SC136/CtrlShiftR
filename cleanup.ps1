# Cleanup Script - Remove unnecessary files
# Review this script before running!

Write-Host "🧹 Cleaning up unnecessary files..." -ForegroundColor Cyan

# Remove duplicate documentation files (keeping README.md and COMPLETE_SETUP.md)
$docsToRemove = @(
    "doc.md",
    "FINAL_SUMMARY.md",
    "PRODUCTION_DEPLOYMENT.md",
    "PROJECT_README.md",
    "QUICKSTART.md",
    "QUICKSTART_GUIDE.md",
    "QUICK_REFERENCE.md",
    "SETUP_GUIDE.md",
    "ARCHITECTURE.md",
    "TESTING_GUIDE.md"
)

foreach ($file in $docsToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✓ Removed $file" -ForegroundColor Yellow
    }
}

# Remove test files
$testFiles = @(
    "test_all.ps1",
    "reasoning_layer\test_final.py",
    "reasoning_layer\main_demo.py",
    "reasoning_layer\sample_high_confidence.json",
    "reasoning_layer\sample_low_confidence.json",
    "reasoning_layer\sample_unknown_issue.json",
    "image_classifier\test_components.py"
)

foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✓ Removed $file" -ForegroundColor Yellow
    }
}

# Remove duplicate start scripts (keeping start_all.ps1)
$scriptsToRemove = @(
    "quick_start.ps1",
    "start_production.ps1",
    "start_services.ps1"
)

foreach ($file in $scriptsToRemove) {
    if (Test-Path $file) {
        Remove-Item $file -Force
        Write-Host "  ✓ Removed $file" -ForegroundColor Yellow
    }
}

# Remove Python cache directories
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
Write-Host "  ✓ Removed __pycache__ directories" -ForegroundColor Yellow

Write-Host "`n✅ Cleanup complete!" -ForegroundColor Green
Write-Host "`nKept important files:" -ForegroundColor Cyan
Write-Host "  • README.md - Main documentation" -ForegroundColor White
Write-Host "  • COMPLETE_SETUP.md - Setup guide" -ForegroundColor White
Write-Host "  • start_all.ps1 - Service startup script" -ForegroundColor White
Write-Host "  • stop_all.ps1 - Service stop script" -ForegroundColor White
Write-Host "  • train_model.ps1 - Model training script" -ForegroundColor White
Write-Host "  • All source code and models" -ForegroundColor White
