# SecureMedi Startup Guide

This guide reflects the current workspace setup and verified startup flow.

## Current Status

- `START_ALL.ps1`, `START_ALL.bat`, and `START_ALL.sh` are not present in this repo.
- Available startup scripts:
	- `START_GANACHE.bat`
	- `START_BACKEND_WITH_GANACHE.ps1`
- Recommended reliable flow is manual startup in separate terminals.

## Verified Startup Flow (Windows)

### Terminal 1: Start Ganache (port 7545)

Option A:

```powershell
Set-Location "c:\Users\Arnav Anand\SecureMedi"
START_GANACHE.bat
```

Option B:

```powershell
Set-Location "c:\Users\Arnav Anand\SecureMedi"
npx ganache --port 7545 --mnemonic "test test test test test test test test test test test junk" --accounts 10
```

### Terminal 2: Start Backend (port 8000)

```powershell
Set-Location "c:\Users\Arnav Anand\SecureMedi"
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 3: Start Frontend (port 3000)

```powershell
Set-Location "c:\Users\Arnav Anand\SecureMedi\frontend"
if (-not (Test-Path .\node_modules)) { npm install }
npm run dev
```

## URLs

- Backend: http://localhost:8000
- Backend health: http://localhost:8000/health/live
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Ganache RPC: http://127.0.0.1:7545

## Quick Checks

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/health/live
Invoke-WebRequest -UseBasicParsing http://localhost:3000
```

## Troubleshooting

### Port already in use

```powershell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 7545 -State Listen).OwningProcess -Force
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000 -State Listen).OwningProcess -Force
Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000 -State Listen).OwningProcess -Force
```

### Missing Python virtual environment

```powershell
Set-Location "c:\Users\Arnav Anand\SecureMedi"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

### Missing frontend dependencies

```powershell
Set-Location "c:\Users\Arnav Anand\SecureMedi\frontend"
npm install
```

## Stop Services

- Press `Ctrl+C` in each running terminal.
