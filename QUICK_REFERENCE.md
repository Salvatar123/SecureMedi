# SecureMedi Setup - One Page Quick Reference

## Prerequisites
- Ganache running: `ganache-cli --deterministic --accounts 10 --port 7545` (Terminal 1)
- Virtual environment activated: `.\venv\Scripts\Activate.ps1`
- Dependencies installed: `pip install -r requirements.txt`

---

## Complete Setup in 3 Steps

### Step 1️⃣: View Ganache Accounts
```powershell
python setup_ganache_accounts.py
```
**See:** All 10 Ganache accounts with balances

---

### Step 2️⃣: Run Complete Setup (MASTER SCRIPT)
```powershell
python setup_complete.py
```
**Does:** Verifies environment → Connects Ganache → Deploys contract → Validates config → Checks readiness

**Expected Output:** All green checkmarks ✓

---

### Step 3️⃣: Start Application
```powershell
python main.py
```
**Runs:** Real-time sensor monitoring → Anomaly detection → CSV logging → Blockchain alerts

**See:** Continuous vital data and ALERT messages

---

### OPTIONAL - Step 4️⃣: Start New Dashboard (v2.0)
```powershell
cd frontend
npm install
npm run dev
```
**Opens:** http://localhost:3000 - Modern React dashboard

With Backend:
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

---

## Terminal Layout

| Terminal 1 | Terminal 2 | Terminal 3 |
|-----------|-----------|----------|
| Ganache (Port 7545) | Setup & Application | Dashboard v2.0 |
| `ganache-cli ...` | `python setup_complete.py` | `npm run dev` (frontend) |
| Keep running | Run setup first | Backend: uvicorn :8000 |

---

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Cannot connect to Ganache" | Start Ganache in Terminal 1 first |
| "Module not found" | Run `pip install -r requirements.txt` |
| "Port 7545 in use" | Close other apps using it or restart system |
| "Port 3000 in use" | Change port in frontend or kill existing process |
| "Port 8000 in use" | Backend already running, check `netstat -ano` |

---

## Files Created/Updated

📄 **setup_ganache_accounts.py** - View Ganache accounts  
📄 **setup_complete.py** - Master setup automating all steps  
📄 **compile_and_deploy.py** - Smart contract deployment (called by setup_complete.py)  
📄 **logs/data.csv** - Health data output (auto-created)  
📄 **.env** - Configuration (auto-updated by setup)  

---

## What Gets Generated

```
After Running setup_complete.py:
✓ Ganache connection verified
✓ Smart contract deployed to blockchain
✓ .env updated with CONTRACT_ADDRESS
✓ logs/ directory confirmed
✓ System ready to run

After Running main.py:
✓ Real-time vitals generated every 5 seconds
✓ Anomalies detected
✓ Data logged to logs/data.csv
✓ ALERT status triggers blockchain transaction

After Opening Dashboard:
✓ Web interface at http://localhost:8501
✓ View live vital data
✓ See access logs
✓ Manage accounts
```

---

## Success Indicators

✅ **setup_complete.py:** All 5 steps show green checkmarks
✅ **main.py:** Shows "Vitals: {'heart': X, 'temp': Y, 'spo2': Z}" every 5 seconds
✅ **dashboard:** Opens without errors at localhost:8501
✅ **logs/data.csv:** File grows with new records

---

## Done! 🚀

Your SecureMedi system is now:
- ✓ Configured
- ✓ Deployed
- ✓ Running locally
- ✓ Ready for testing

Monitor the output and check the logs directory for generated data.
