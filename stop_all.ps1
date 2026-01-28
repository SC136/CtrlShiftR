# ========================================
# 🌾 FARMER ASSISTANT - STOP ALL SERVICES
# ========================================

Write-Host "🛑 Stopping all Farmer Assistant services..." -ForegroundColor Yellow

# Ports to clean up
$ports = @(8000, 8002, 8081, 19000, 19001, 19002)

foreach ($port in $ports) {
    $connections = netstat -ano | Select-String ":$port.*LISTENING"
    if ($connections) {
        $connections | ForEach-Object {
            if ($_ -match '\s+(\d+)$') {
                $pid = $matches[1]
                try {
                    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($process) {
                        Stop-Process -Id $pid -Force
                        Write-Host "✅ Stopped process $pid on port $port ($($process.ProcessName))" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "⚠️  Could not stop process $pid" -ForegroundColor Yellow
                }
            }
        }
    }
}

# Kill any remaining Python/Node processes related to our project
Write-Host "`n🧹 Cleaning up related processes..." -ForegroundColor Cyan
$processes = @("uvicorn", "expo")
foreach ($procName in $processes) {
    $procs = Get-Process -Name $procName -ErrorAction SilentlyContinue
    if ($procs) {
        $procs | ForEach-Object {
            Stop-Process -Id $_.Id -Force
            Write-Host "✅ Stopped $procName (PID: $($_.Id))" -ForegroundColor Green
        }
    }
}

Write-Host "`n✅ All services stopped!" -ForegroundColor Green
Start-Sleep -Seconds 2
