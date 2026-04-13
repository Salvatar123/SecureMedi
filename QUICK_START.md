# Quick Reference - Starting SecureMedi

## Fast Path (Windows)

### Terminal 1: Ganache

```powershell
Set-Location "c:\Users\Arnav Anand\SecureMedi"
npx ganache --port 7545 --mnemonic "test test test test test test test test test test test junk" --accounts 10
```

### Terminal 2: Backend

```powershell
Set-Location "c:\Users\Arnav Anand\SecureMedi"
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 3: Frontend

```powershell
Set-Location "c:\Users\Arnav Anand\SecureMedi\frontend"
if (-not (Test-Path .\node_modules)) { npm install }
npm run dev
```

## URLs

- API: http://localhost:8000
- API docs: http://localhost:8000/docs
- App: http://localhost:3000
- Ganache RPC: http://127.0.0.1:7545

## Health Checks

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/health/live
Invoke-WebRequest -UseBasicParsing http://localhost:3000
```

## Notes

- `START_ALL.ps1`, `START_ALL.bat`, and `START_ALL.sh` are not in this repository.
- Existing scripts you can still use:
  - `START_GANACHE.bat`
  - `START_BACKEND_WITH_GANACHE.ps1`

## More Help

- [STARTUP_GUIDE.md](STARTUP_GUIDE.md)
- [documentation/LOCAL_SETUP.md](documentation/LOCAL_SETUP.md)
