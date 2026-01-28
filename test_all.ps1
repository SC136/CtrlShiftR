# ========================================
# 🌾 FARMER ASSISTANT - TEST ALL SERVICES
# ========================================

Write-Host "=" * 70 -ForegroundColor Green
Write-Host "🌾 FARMER ASSISTANT - SERVICE TESTING" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Green

$testsPassed = 0
$testsFailed = 0

function Test-Service {
    param(
        [string]$Name,
        [string]$URL,
        [int]$ExpectedStatus = 200
    )
    
    Write-Host "`n🧪 Testing: $Name" -ForegroundColor Cyan
    Write-Host "   URL: $URL" -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri $URL -Method GET -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "   ✅ PASSED - Status: $($response.StatusCode)" -ForegroundColor Green
            Write-Host "   Response: $($response.Content.Substring(0, [Math]::Min(100, $response.Content.Length)))..." -ForegroundColor Gray
            return $true
        } else {
            Write-Host "   ❌ FAILED - Unexpected status: $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "   ❌ FAILED - Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

function Test-Port {
    param(
        [string]$Name,
        [int]$Port
    )
    
    Write-Host "`n🔌 Checking Port: $Port ($Name)" -ForegroundColor Cyan
    
    $listening = netstat -ano | Select-String ":$Port.*LISTENING"
    if ($listening) {
        Write-Host "   ✅ PASSED - Service is listening on port $Port" -ForegroundColor Green
        return $true
    } else {
        Write-Host "   ❌ FAILED - No service listening on port $Port" -ForegroundColor Red
        return $false
    }
}

# Test 1: Check if services are running on correct ports
Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "TEST SUITE 1: PORT CHECKS" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

if (Test-Port -Name "Image Classifier API" -Port 8000) { $testsPassed++ } else { $testsFailed++ }
if (Test-Port -Name "Reasoning Layer API" -Port 8002) { $testsPassed++ } else { $testsFailed++ }
if (Test-Port -Name "Expo Dev Server" -Port 8081) { $testsPassed++ } else { $testsFailed++ }

# Test 2: HTTP endpoint checks
Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "TEST SUITE 2: API ENDPOINT CHECKS" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

if (Test-Service -Name "Image Classifier Health" -URL "http://localhost:8000/health") { $testsPassed++ } else { $testsFailed++ }
if (Test-Service -Name "Image Classifier Root" -URL "http://localhost:8000/") { $testsPassed++ } else { $testsFailed++ }

# Test 3: Check if model is loaded
Write-Host "`n🧪 Testing: Model Status" -ForegroundColor Cyan
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -UseBasicParsing
    $healthData = $healthResponse.Content | ConvertFrom-Json
    
    if ($healthData.model_loaded -eq $true) {
        Write-Host "   ✅ PASSED - Model is loaded and ready" -ForegroundColor Green
        Write-Host "   Classes: $($healthData.num_classes)" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "   ⚠️  WARNING - Model not loaded (train model first)" -ForegroundColor Yellow
        Write-Host "   Run: .\train_model.ps1" -ForegroundColor Yellow
        $testsFailed++
    }
} catch {
    Write-Host "   ❌ FAILED - Could not check model status" -ForegroundColor Red
    $testsFailed++
}

# Test 4: Check critical files
Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "TEST SUITE 3: FILE EXISTENCE CHECKS" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

$criticalFiles = @(
    @{Path="image_classifier\api.py"; Name="Image Classifier API"},
    @{Path="reasoning_layer\main.py"; Name="Reasoning Layer API"},
    @{Path="atharva_UI\App.tsx"; Name="Expo App Entry"},
    @{Path="atharva_UI\services\api.ts"; Name="API Configuration"},
    @{Path=".venv\Scripts\python.exe"; Name="Virtual Environment"}
)

foreach ($file in $criticalFiles) {
    Write-Host "`n📄 Checking: $($file.Name)" -ForegroundColor Cyan
    if (Test-Path $file.Path) {
        Write-Host "   ✅ PASSED - Found: $($file.Path)" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "   ❌ FAILED - Missing: $($file.Path)" -ForegroundColor Red
        $testsFailed++
    }
}

# Test 5: Check dependencies
Write-Host "`n" + ("=" * 70) -ForegroundColor Cyan
Write-Host "TEST SUITE 4: DEPENDENCY CHECKS" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan

Write-Host "`n🐍 Python Packages:" -ForegroundColor Cyan
$packages = @("torch", "fastapi", "uvicorn", "pillow")
foreach ($pkg in $packages) {
    $result = & ".venv\Scripts\python.exe" -c "import $pkg; print('OK')" 2>&1
    if ($result -match "OK") {
        Write-Host "   ✅ $pkg installed" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "   ❌ $pkg missing" -ForegroundColor Red
        $testsFailed++
    }
}

Write-Host "`n📦 Node.js Dependencies:" -ForegroundColor Cyan
if (Test-Path "atharva_UI\node_modules") {
    Write-Host "   ✅ node_modules exists" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "   ❌ node_modules missing - run: cd atharva_UI; npm install" -ForegroundColor Red
    $testsFailed++
}

# Summary
Write-Host "`n" + ("=" * 70) -ForegroundColor Green
Write-Host "TEST SUMMARY" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Green

$totalTests = $testsPassed + $testsFailed
$passRate = if ($totalTests -gt 0) { [math]::Round(($testsPassed / $totalTests) * 100, 1) } else { 0 }

Write-Host "`n📊 Results:" -ForegroundColor Cyan
Write-Host "   • Total Tests: $totalTests" -ForegroundColor White
Write-Host "   • Passed: $testsPassed" -ForegroundColor Green
Write-Host "   • Failed: $testsFailed" -ForegroundColor Red
Write-Host "   • Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 80) { "Green" } elseif ($passRate -ge 60) { "Yellow" } else { "Red" })

if ($testsFailed -eq 0) {
    Write-Host "`n✅ ALL TESTS PASSED! System is ready." -ForegroundColor Green
} elseif ($testsFailed -le 2) {
    Write-Host "`n⚠️  MINOR ISSUES DETECTED - System should work with limitations" -ForegroundColor Yellow
} else {
    Write-Host "`n❌ CRITICAL ISSUES DETECTED - Please fix errors above" -ForegroundColor Red
}

Write-Host ("`n" + ("=" * 70)) -ForegroundColor Green
Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
