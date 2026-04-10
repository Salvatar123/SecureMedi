#!/usr/bin/env pwsh
param(
    [int]$GanachePort = 7545,
    [int]$BackendPort = 8000
)

$ErrorActionPreference = "Continue"
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Red = [System.ConsoleColor]::Red

Write-Host "`n════════════════════════════════════════" -ForegroundColor $Green
Write-Host "SecureMedi - Backend + Ganache Startup" -ForegroundColor $Green
Write-Host "════════════════════════════════════════`n" -ForegroundColor $Green

# Get Python path
$pythonExe = Resolve-Path ".\.venv\Scripts\python.exe" -ErrorAction SilentlyContinue

if (-not $pythonExe) {
    Write-Host "Error: Virtual environment not found at .venv" -ForegroundColor $Red
    exit 1
}

Write-Host "Using Python: $pythonExe" -ForegroundColor $Green

# Step 1: Start Ganache
Write-Host ""
Write-Host "Starting Ganache on port $GanachePort..." -ForegroundColor $Yellow

$batchFile = Join-Path $env:TEMP "ganache_$GanachePort.bat"
$batchContent = '@echo off' + "`r`n" +
    'echo Starting Ganache...' + "`r`n" +
    'set MOD=test test test test test test test test test test test junk' + "`r`n" +
    "where ganache-cli >nul 2>&1 || where ganache >nul 2>&1 || npm list -g ganache" + "`r`n" +
    'pause'

[System.IO.File]::WriteAllText($batchFile, $batchContent, [System.Text.Encoding]::ASCII)

$ganacheProc = Start-Process $batchFile -PassThru
Write-Host "Ganache started (PID: $($ganacheProc.Id))" -ForegroundColor $Green

Write-Host "Waiting for Ganache (5 seconds)..." -ForegroundColor $Yellow
Start-Sleep -Seconds 5

Write-Host "Starting Backend..." -ForegroundColor $Green
Write-Host "════════════════════════════════════════`n" -ForegroundColor $Green

trap {
    Write-Host "`nShutting down..." -ForegroundColor $Yellow
    if ($ganacheProc) { Stop-Process -Id $ganacheProc.Id -EA SilentlyContinue }
    if (Test-Path $batchFile) { Remove-Item $batchFile -EA SilentlyContinue }
    break
}

& $pythonExe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port $BackendPort
