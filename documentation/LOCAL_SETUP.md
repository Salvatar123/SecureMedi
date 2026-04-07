# 🚀 Local Setup Guide - SecureMedi with Blockchain

This guide walks you through running the complete SecureMedi system locally with full blockchain integration.

---

## ✅ Prerequisites

- ✅ Python 3.10+ (you have 3.13.5)
- ✅ Virtual environment activated
- ✅ Dependencies installed (web3, pandas, fastapi)

---

## 📋 Complete Setup Steps

### **Step 1: Set Up Local Blockchain (Ganache)**

**For Windows - Recommended: Use Ganache GUI**

1. Download Ganache GUI: https://trufflesuite.com/ganache/
2. Run Ganache
3. In Settings → Server tab:
   - Set Hostname to: `127.0.0.1`
   - Set Port to: `7545`
4. Click "Save and Restart"
5. Keep Ganache running in background

**Alternative: Use ganache-cli (if you have Node.js)**

```powershell
npm install -g ganache-cli
ganache-cli --deterministic --accounts 10 --port 7545
```

✅ **Check Ganache is running:**
```powershell
curl http://127.0.0.1:7545
# Should return something like: {"jsonrpc":"2.0","id":1,"error":{"code":-32700,"message":"Parse error"}}
```

---

### **Step 2: Deploy Smart Contract**

**Option A: Easiest - Use Remix IDE (Recommended for Windows)**

1. Open: https://remix.ethereum.org/
2. Create new file: `Healthlogger.sol`
3. Copy entire content from `contracts/Healthlogger.sol` (in this workspace)
4. In Remix:
   - Go to "Solidity Compiler" tab
   - Click "Compile Healthlogger.sol"
   - Go to "Deploy & Run Transactions" tab
   - Environment: Select "Injected Provider - Ganache"
   - Contract: Select "SecureMedi"
   - Click "Deploy"
5. Copy the deployed contract address (e.g., `0x1234...`)

**Option B: Use Python Deployment Script**

```powershell
& "c:/Users/Arnav Anand/SecureMedi/.venv/Scripts/python.exe" deploy_contract.py
```

⚠️ **Note:** This requires the contract to be pre-compiled with bytecode.

---

### **Step 3: Configure Environment**

1. Update `.env` file:

```env
# Enable blockchain
ENABLE_BLOCKCHAIN=True

# Blockchain settings
GANACHE_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=0x<PASTE_YOUR_CONTRACT_ADDRESS_HERE>
PRIVATE_KEY=0x<GANACHE_ACCOUNT_1_PRIVATE_KEY>

# Other settings
ENABLE_LOCAL_LOGGING=True
SENSOR_INTERVAL_SEC=5
DEFAULT_PATIENT_ID=P001
```

**To get Ganache private key from GUI:**
- Open Ganache → Click on account key icon
- Copy the private key (starts with `0x`)

---

### **Step 4: Run the Full Application**

**Terminal 1 - Start Main Monitoring System**

```powershell
cd C:\Users\Arnav Anand\SecureMedi
& ".\.venv\Scripts\Activate.ps1"
& ".\.venv\Scripts\python.exe" main.py
```

**Expected Output:**
```
2026-03-24 18:56:53,336 - __main__ - INFO - 🚀 secureMedi System Started...
2026-03-24 18:56:53,336 - services.detector_service - WARNING - Alert: Temperature 38.5 > 38.0
2026-03-24 18:56:53,336 - __main__ - INFO - Vitals: {'heart': 64, 'temp': 38.5, 'spo2': 88}
2026-03-24 18:56:53,336 - __main__ - INFO - Status: ALERT
2026-03-24 18:56:53,337 - __main__ - INFO - ✅ Alert stored on Blockchain: 0xabc123...
```

**Terminal 2 - Start Backend API**

```powershell
cd C:\Users\Arnav Anand\SecureMedi\backend
& "C:\Users\Arnav Anand\SecureMedi\.venv\Scripts\Activate.ps1"
python -m uvicorn app.main:app --reload --port 8000
```

API available at: **http://localhost:8000**
API Docs: **http://localhost:8000/docs**

**Terminal 3 - Start Dashboard (Next.js v2.0)**

```powershell
cd C:\Users\Arnav Anand\SecureMedi\frontend
npm install  # Only needed first time
npm run dev
```

Dashboard available at: **http://localhost:3000**

---

## 🧪 Testing Blockchain Integration

Once both services are running:

1. **Check Main App Output:**
   - Look for "ALERT" status messages
   - Should see "✅ Alert stored on Blockchain: 0x..." transactions
   - Transactions happen when vitals exceed thresholds

2. **Verify in Ganache:**
   - Open Ganache GUI
   - Go to "Transactions" tab
   - Should see new transactions from deployment + alerts

3. **Check Local Logs:**
   - Open `logs/data.csv`
   - Should see vitals being logged

4. **Check Dashboard:**
   - Navigate to http://localhost:8501
   - View real-time vitals and alerts
   - See blockchain transaction history

---

## 🐛 Troubleshooting

### ❌ "Cannot connect to blockchain at http://127.0.0.1:7545"

**Solution:**
```powershell
# Check if Ganache is running
curl http://127.0.0.1:7545

# If not working:
# 1. Open Ganache GUI and verify port is 7545
# 2. Check Windows Firewall isn't blocking port 7545
# 3. Restart Ganache
```

### ❌ "Contract not found at address..."

**Solution:**
1. Deploy contract using Remix IDE (Step 2)
2. Update `CONTRACT_ADDRESS` in `.env`
3. Restart main.py

### ❌ Application runs but no blockchain transactions

**Solution:**
1. Verify `ENABLE_BLOCKCHAIN=True` in `.env`
2. Check logs for errors
3. Ensure `CONTRACT_ADDRESS` is set correctly
4. Confirm Ganache is still running

### ❌ Dashboard shows no data

**Solution:**
```powershell
# Check if logs directory and CSV exist
dir logs/
cat logs/data.csv

# If empty, wait a few seconds for data to be generated
# It logs every SENSOR_INTERVAL_SEC (default 5 seconds)
```

---

## 📊 System Architecture

```
Sensors (Simulated)
    ↓
Edge AI (Anomaly Detection)
    ↓
Local CSV Logs
    ↓
Blockchain (Alerts Only)
    ↓
Dashboard (Visualization)
```

---

## 🎯 Next Steps

After verifying everything works locally:

1. Run integration tests:
```powershell
pytest tests/ -v
```

2. Review logs:
```powershell
tail -f logs/data.csv
```

3. Ready for deployment! See `DEPLOYMENT.md`

---

## 📞 Support

- Check logs for detailed errors
- Verify all services are running
- Confirm .env settings match your Ganache setup
