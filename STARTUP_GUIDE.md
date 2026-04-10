# SecureMedi - Startup Scripts

Quick startup scripts to run both backend and frontend services.

## Quick Start

### Windows (PowerShell) - Recommended
```powershell
.\START_ALL.ps1
```

**Features:**
- ✅ Starts backend first
- ✅ Waits for backend to be ready (checks port 8000)
- ✅ Then starts frontend
- ✅ Shows URLs and API docs links
- ✅ Automatic cleanup on existing processes
- ✅ Colored output

**Usage:**
```powershell
# Default: Start both backend and frontend
.\START_ALL.ps1

# Skip backend (only start frontend)
.\START_ALL.ps1 -SkipBackend

# Skip frontend (only start backend)
.\START_ALL.ps1 -SkipFrontend

# Custom ports
.\START_ALL.ps1 -BackendPort 8001 -FrontendPort 3001
```

**Requirements:**
- Virtual environment exists at `.venv`
- Backend dependencies installed: `pip install -r requirements.txt`
- Frontend dependencies installed: `cd frontend && npm install`

### Windows (Batch File)
```batch
START_ALL.bat
```

Simple batch version that opens backend and frontend in separate command windows.

### Linux / macOS
```bash
chmod +x START_ALL.sh
./START_ALL.sh
```

**Features:**
- ✅ Full shell script with proper error handling
- ✅ Automatic port availability checking (uses `nc` and `lsof`)
- ✅ Process management
- ✅ Colored output

## What Each Script Does

### Backend Startup
1. ✓ Activates Python virtual environment (`.venv`)
2. ✓ Starts uvicorn server on port 8000
3. ✓ Watches for code changes (auto-reload)
4. ✓ Makes API docs available at `http://localhost:8000/docs`

### Frontend Startup
1. ✓ Installs dependencies (if needed)
2. ✓ Starts Next.js dev server on port 3000
3. ✓ Watches for code changes (hot reload)
4. ✓ Makes app available at `http://localhost:3000`

## URLs After Startup

| Service | URL | Notes |
|---------|-----|-------|
| **Backend** | http://localhost:8000 | FastAPI server |
| **API Docs** | http://localhost:8000/docs | Swagger UI with all endpoints |
| **API ReDoc** | http://localhost:8000/redoc | Alternative API documentation |
| **Frontend** | http://localhost:3000 | Next.js application |

## Manual Alternative (If Scripts Don't Work)

### Terminal 1: Start Backend
```bash
# Activate virtual environment
.venv\Scripts\Activate.ps1          # Windows PowerShell
source .venv/bin/activate            # Linux/Mac

# Start backend
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Start Frontend
```bash
cd frontend
npm run dev
```

## Troubleshooting

### "Port already in use" Error
```powershell
# Kill process using port 8000 (backend)
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000 -State Listen).OwningProcess -Force

# Kill process using port 3000 (frontend)
Stop-Process -Id (Get-NetTCPConnection -LocalPort 3000 -State Listen).OwningProcess -Force
```

### "Virtual environment not found"
```bash
# Create virtual environment
python -m venv .venv

# Activate and install dependencies
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac

pip install -r requirements.txt
```

### "node_modules not found"
```bash
cd frontend
npm install
cd ..
```

### Backend not starting
1. Check Python is installed: `python --version`
2. Check requirements: `pip install -r requirements.txt`
3. Check port 8000 is free: `netstat -ano | findstr :8000`

### Frontend not starting
1. Check Node.js is installed: `node --version`
2. Check npm is installed: `npm --version`
3. Install dependencies: `cd frontend && npm install`

## Environment Variables

Create `.env` file in root for backend configuration:

```env
# Backend FastAPI
FASTAPI_ENV=development
JWT_PRIVATE_KEY=your_private_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Optional: Database
DATABASE_URL=postgresql://user:password@localhost/securemedi

# Optional: Blockchain
WEB3_PROVIDER_URI=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x...
PRIVATE_KEY=0x...
```

Frontend `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Stopping Services

- **Windows:** Close the command windows or press `Ctrl+C` in each
- **Linux/Mac:** Press `Ctrl+C` in the terminal

## Development Tips

- **Backend auto-reload:** Code changes automatically restart the server (`--reload` flag)
- **Frontend hot reload:** Code changes instantly appear in browser (Next.js built-in)
- **Database:** Set up Supabase or PostgreSQL for persistent storage
- **Blockchain:** Run Ganache separately for local blockchain testing

## Performance Notes

- First startup takes 30-60 seconds (Node.js compilation)
- Subsequent restarts are much faster
- Backend API docs load at `http://localhost:8000/docs` after startup
- Frontend ready when you see `compiled client and server successfully`

## Production Deployment

These scripts are for **development only**. For production:

1. Use Docker Compose: `docker-compose up` (see [docker-compose.yml](../docker-compose.yml))
2. Use process managers like PM2 or systemd
3. Use HTTPS (Let's Encrypt) instead of HTTP
4. Deploy to cloud platforms (Heroku, AWS, DigitalOcean, etc.)

See [DEPLOYMENT.md](../documentation/DEPLOYMENT.md) for full production setup.
