# 🚀 Quick Reference - Starting SecureMedi

## One Command Startup

### Windows PowerShell
```powershell
.\START_ALL.ps1
```

### Windows Command Prompt
```batch
START_ALL.bat
```

### Linux / macOS
```bash
./START_ALL.sh
```

---

## What Happens

```
1. Backend starts on http://localhost:8000
   ↓ (waits for it to be ready)
2. Frontend starts on http://localhost:3000
   ↓
3. Both running! Ready to develop 🎉
```

---

## Services Running

| Service | URL | Docs |
|---------|-----|------|
| **API** | http://localhost:8000 | [Swagger](http://localhost:8000/docs) |
| **App** | http://localhost:3000 | - |

---

## Common Commands

| Task | Command |
|------|---------|
| **Start everything** | `.\START_ALL.ps1` |
| **Just backend** | `.\START_ALL.ps1 -SkipFrontend` |
| **Just frontend** | `.\START_ALL.ps1 -SkipBackend` |
| **Stop services** | `Ctrl+C` in each window |
| **Kill port 8000** | `Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000 -State Listen).OwningProcess -Force` |
| **Kill port 3000** | `Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000 -State Listen).OwningProcess -Force` |

---

## First Time Setup

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install frontend dependencies
cd frontend
npm install
cd ..

# 5. Now you can run
.\START_ALL.ps1
```

---

## Manual Startup (If Scripts Fail)

```bash
# Terminal 1: Backend
.venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## Troubleshooting

**"Port X already in use"**
- Backend may still be running
- Use Task Manager or `netstat` to find and kill it
- Try different ports with `-BackendPort 8001` argument

**"Module not found" errors**
- Reinstall requirements: `pip install -r requirements.txt`
- Clear pip cache: `pip cache purge`

**"npm ERR!" in frontend**
- Clear npm cache: `npm cache clean --force`
- Reinstall: `cd frontend && rm -rf node_modules && npm install`

---

## More Help

- 📖 [Full Startup Guide](STARTUP_GUIDE.md)
- 📚 [Development Documentation](documentation/README.md)
- 🔧 [Configuration Guide](documentation/LOCAL_SETUP.md)
