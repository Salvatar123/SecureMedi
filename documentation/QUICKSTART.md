# SecureMedi Local Setup Guide

Complete step-by-step guide to set up and run SecureMedi locally with blockchain integration.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Setup](#project-setup)
3. [Blockchain Setup (Ganache)](#blockchain-setup-ganache)
4. [Smart Contract Deployment](#smart-contract-deployment)
5. [Application Configuration](#application-configuration)
6. [Running the Application](#running-the-application)
7. [Accessing the Dashboard](#accessing-the-dashboard)
8. [Verification & Testing](#verification--testing)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Windows 10/11** or **macOS/Linux**
- **Python 3.10+** (verify: `python --version`)
- **Node.js & npm** (for Ganache CLI)
- **Git** (optional, for cloning)
- **4GB+ RAM**
- **2GB+ Disk Space**

### Software to Install

```powershell
# Check Python version
python --version
# Should show: Python 3.10+ or 3.11+

# Install Node.js and npm
# Download from: https://nodejs.org/ (LTS version)
# Verify installation:
node --version
npm --version
```

---

## Project Setup

### Step 1: Clone or Navigate to Repository

```powershell
# If you don't have it yet
git clone https://github.com/your-org/securemedi.git
cd securemedi

# Or navigate to existing project
cd C:\Users\YourUsername\SecureMedi
```

### Step 2: Create Python Virtual Environment

```powershell
# Navigate to project root
cd SecureMedi

# Create virtual environment
python -m venv venv

# Activate it (Windows)
.\venv\Scripts\Activate.ps1

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed web3-6.13.0 streamlit-1.28.1 pandas-2.0.3 pydantic-2.7.4 ...
```

### Step 4: Verify Environment

```powershell
# Test Python packages
python -c "import web3, streamlit, pandas, pydantic; print('All packages installed!')"
```

Should output: `All packages installed!`

---

## Blockchain Setup (Ganache)

### Option A: Ganache CLI (Recommended for Development)

#### Step 1: Install Ganache CLI

```powershell
# Install globally via npm
npm install -g ganache-cli

# Verify installation
ganache-cli --version
```

#### Step 2: Start Ganache

```powershell
# Open a NEW PowerShell terminal and run:
ganache-cli --deterministic --accounts 10 --port 7545

# Expected output:
# ganache v7.x.x
# Ganache started
# Available Accounts
# ==================
# (0) 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1 (100 ETH)
# (1) 0xFFcf8FDEE72ac11b5c542428B7a3A3d3B5B6Ec89 (100 ETH)
# ...
```

**Keep this terminal running!** Ganache must stay active.

### Option B: Ganache GUI (Visual Alternative)

1. Download Ganache GUI: https://trufflesuite.com/ganache/
2. Run Ganache application
3. Click "Quickstart Ethereum"
4. Verify it's running on port 7545

---

## Smart Contract Deployment

### Step 1: Deploy Using Python Script

Open a **NEW PowerShell terminal** (keep Ganache running in the previous one):

```powershell
# Activate virtual environment
cd C:\Users\YourUsername\SecureMedi
.\venv\Scripts\Activate.ps1

# Run deployment script
python compile_and_deploy.py
```

**Expected Output:**
```
============================================================
Compiling and Deploying SecureMedi Contract
============================================================

Ensuring Solidity compiler is available...
Compiling contract...
Contract compiled successfully!
Bytecode length: 14114 characters

Connecting to Ganache at http://127.0.0.1:7545...
Connected!

Deploying account: 0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1
Account balance: 100 ETH

Deploying contract...
Transaction sent: f2187ec96c01a1f97d57be1d51b97e27f24483bdaed36634...
Waiting for deployment...

SUCCESS! Contract deployed!
Contract Address: 0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab

Updating .env...
Updated .env: CONTRACT_ADDRESS=0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab

============================================================
DEPLOYMENT COMPLETE!
============================================================
```

### Step 2: Verify Contract Deployment

The `.env` file was automatically updated with the contract address. Verify it:

```powershell
# View .env file
Get-Content .env | Select-String "CONTRACT_ADDRESS"

# Should show:
# CONTRACT_ADDRESS=0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab
```

---

## Application Configuration

### Step 1: Check .env File

```powershell
Get-Content .env
```

Should contain:

```env
ENVIRONMENT=development
ENABLE_BLOCKCHAIN=True
ENABLE_LOCAL_LOGGING=True

GANACHE_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab
PRIVATE_KEY=0x4f531878d488cb41e18550a0ac6fd76e16531616fef79972b098bc00548d4c51

LOG_FILE=logs/data.csv
SENSOR_INTERVAL_SEC=5
HEART_RATE_MAX=110
TEMPERATURE_MAX=38.0
SPO2_MIN=92
```

### Step 2: Create Logs Directory (if needed)

```powershell
# Create logs folder
mkdir logs -Force

# Verify
ls -Name logs/
```

---

## Running the Application

### Recommended: Use Startup Scripts (Automatic)

The easiest way - starts backend and frontend automatically in the correct order:

**Windows PowerShell:**
```powershell
.\START_ALL.ps1
```

**Windows Command Prompt:**
```batch
START_ALL.bat
```

**Linux/macOS:**
```bash
./START_ALL.sh
```

This single command will:
- ✅ Start FastAPI backend on http://localhost:8000
- ✅ Wait for it to be ready
- ✅ Start Next.js frontend on http://localhost:3000
- ✅ Show you the URLs to access

See [STARTUP_GUIDE.md](../STARTUP_GUIDE.md) for more startup options.

---

### Alternative: Manual Startup (3 Terminals)

If you prefer to manage startup manually:

**You need 3 terminal windows:**
1. **Terminal 1**: Ganache (blockchain) - KEEP RUNNING
2. **Terminal 2**: FastAPI Backend (http://localhost:8000)
3. **Terminal 3**: Next.js Frontend (http://localhost:3000)

#### Terminal 2: Start Backend

```powershell
# From project directory with venv activated
.\venv\Scripts\Activate.ps1
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### Terminal 3: Start Frontend

```powershell
cd frontend
npm run dev
```

**Expected Output:**
```
> next dev
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

## Accessing the Application

### Web Dashboard

Once both services are running:

- **Frontend App:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs (interactive Swagger UI)

### Optional: Legacy Streamlit Dashboard

If you want to use the old Streamlit dashboard instead of the new Next.js frontend:

```powershell
# In a new terminal
.\venv\Scripts\Activate.ps1
streamlit run dashboard/app.py
```

Access at: http://localhost:8501

  For better performance, install Python 3.11.
```

### Access Dashboard

Open in browser: **http://localhost:8501**

**Dashboard Tabs:**
- **Login**: Authenticate with blockchain keys
- **Doctor Panel**: Manage access keys and patient records
- **Patient Portal**: View health data and access logs

---

## Verification & Testing

### Check Vitals are Being Logged

**Terminal 1 (Main App):** Should show continuous updates:
```
Vitals: {'heart': 95, 'temp': 37.5, 'spo2': 97}
Status: NORMAL
```

### Check CSV Data

```powershell
# View latest entries
Get-Content logs/data.csv -Tail 5

# Expected format:
# timestamp,heart,temp,spo2,status
# 2026-03-24T10:30:46.234567,75,37.2,98,NORMAL
# 2026-03-24T10:30:51.456789,112,38.5,91,ALERT
```

### Check Ganache Transactions

In **Ganache GUI or Terminal 1 (Ganache):**
- Should see transaction activity
- Deployment transaction from contract deployment
- Additional transactions when ALERT status occurs

### Run Tests (Optional)

```powershell
# Run test suite
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# View coverage report (opens browser)
start htmlcov/index.html
```

---

## System Architecture Running

```
┌─────────────────────────────────────┐
│   Terminal 1: Ganache (Port 7545)   │
│   (Blockchain Network)               │
└────────────────┬────────────────────┘
                 │
                 ├──────────────────────┐
                 │                      │
    ┌────────────▼──────────┐  ┌───────▼─────────────┐
    │ Terminal 2: main.py   │  │ Terminal 3: Streamlit│
    │ • Sensor Data Gen     │  │ • Web Dashboard      │
    │ • Anomaly Detection   │  │ • Port 8501          │
    │ • CSV Logging         │  │ • User Interface     │
    │ • Blockchain Alerts   │  │                      │
    └───────────────────────┘  └──────────────────────┘
                 │                      │
                 └──────────┬───────────┘
                            │
                    ┌───────▼────────┐
                    │  logs/data.csv │
                    │  (Health Data) │
                    └────────────────┘
```

---

## Quick Summary: All Steps at Once

**Terminal 1 - Ganache:**
```powershell
ganache-cli --deterministic --accounts 10 --port 7545
# Keep running
```

**Terminal 2 - Deploy & Run App:**
```powershell
cd C:\Users\YourUsername\SecureMedi
.\venv\Scripts\Activate.ps1
python compile_and_deploy.py
python main.py
```

**Terminal 3 - Dashboard:**
```powershell
cd C:\Users\YourUsername\SecureMedi
.\venv\Scripts\Activate.ps1
streamlit run dashboard/app.py
```

---

## Troubleshooting

### "Cannot connect to blockchain at http://127.0.0.1:7545"

**Solution:**
- Check Terminal 1: Is Ganache running?
- Check port 7545 is available: `netstat -ano | findstr :7545`
- Restart Ganache with: `ganache-cli --deterministic --accounts 10 --port 7545`

### "Module not found: web3/streamlit/pandas"

**Solution:**
```powershell
# Ensure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt
```

### "Contract not found at address"

**Solution:**
```powershell
# Redeploy contract
python compile_and_deploy.py

# Verify .env was updated
Get-Content .env | Select-String "CONTRACT_ADDRESS"
```

### Streamlit "Port 8501 already in use"

**Solution:**
```powershell
# Kill process on port 8501
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Or use different port
streamlit run dashboard/app.py --server.port 8502
```

### CSV file read errors

**Solution:**
```powershell
# Check logs directory exists
ls logs/

# Create if needed
mkdir logs

# Check permissions
attrib logs/data.csv
```

---

## Next Steps

1. **Monitor System**: Watch Terminal 2 for vital data generation
2. **Access Dashboard**: Open http://localhost:8501 in browser
3. **Check Data**: View `logs/data.csv` for persistent records
4. **Verify Blockchain**: See Ganache transactions in Terminal 1
5. **Run Tests**: Execute `pytest tests/ -v` to validate system

---

## Project Structure

```
SecureMedi/
├── main.py                      # Main application entry point
├── compile_and_deploy.py        # Contract deployment script
├── dashboard/app.py             # Streamlit web interface
├── config/settings.py           # Configuration management
├── services/
│   ├── detector_service.py      # Anomaly detection
│   ├── logger_service.py        # CSV logging
│   └── blockchain_service.py    # Blockchain operations
├── contracts/
│   ├── Healthlogger.sol         # Smart contract
│   └── abi.json                 # Contract ABI
├── logs/data.csv                # Generated health data
├── .env                         # Environment configuration
├── requirements.txt             # Python dependencies
└── documentation/               # Setup guides
```

---

## Support

For issues:
1. Check logs in Terminal 2 output
2. Review troubleshooting section above
3. Verify all prerequisites are installed
4. Ensure no port conflicts (7545 for Ganache, 8501 for Streamlit)

---

## You're All Set! 🚀

Your SecureMedi system is now ready for local development and testing with full blockchain integration.
