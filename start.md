# 🚀 secureMedi – Startup & Demo Guide

This guide explains how to run the **secureMedi** project from scratch for demo or evaluation.

---

## ✅ Prerequisites

Make sure you have installed:

* Python 3.9+
* Ganache (GUI)
* Web Browser (for Remix + Dashboard)
* Git (optional)

---

## 📁 Project Structure

Ensure your folder looks like this:

```
SecureMedi/
│
├── blockchain/
│   └── connector.py
├── contracts/
│   └── abi.json
├── dashboard/
│   └── app.py
├── edge_ai/
├── logs/
├── main.py
├── requirements.txt
└── README.md
```

---

## 🔧 Step 1: Start Ganache (Blockchain)

1. Open Ganache
2. Click **Quickstart Ethereum**
3. Keep Ganache running
4. Confirm RPC URL:

```
http://127.0.0.1:7545
```

---

## 📝 Step 2: Deploy Smart Contract (Remix)

> ⚠️ Do this every time Ganache is restarted.

1. Open [https://remix.ethereum.org](https://remix.ethereum.org)
2. Connect Environment → Custom Provider
3. Enter:

```
http://127.0.0.1:7545
```

4. Compile contract (Solidity 0.8.17, EVM: Istanbul)

5. Deploy contract

6. Copy:

   * Contract Address
   * ABI

7. Save ABI in:

```
contracts/abi.json
```

8. Paste Contract Address in:

```
blockchain/connector.py
```

9. Authorize device:

```
addDevice(your_account_address)
```

---

## 📦 Step 3: Install Dependencies (First Time Only)

Run in project root:

```bash
pip install -r requirements.txt
```

---

## ▶️ Step 4: Start Sensor + Blockchain System

In terminal (project root):

```bash
python main.py
```

Expected output:

```
secureMedi System Started...
Vitals: {...}
Status: NORMAL/ALERT
```

---

## 📊 Step 5: Start Dashboard

Open a new terminal and run:

```bash
streamlit run dashboard/app.py
```

Dashboard will open in browser.

---

## 🎬 Demo Setup (Recommended Order)

1. Start Ganache
2. Deploy contract in Remix
3. Run main.py
4. Run dashboard
5. Show blockchain transactions
6. Stop using Ctrl + C

---

## 🛑 Stopping the System

To stop safely:

Press in each terminal:

```
Ctrl + C
```

---

## ⚠️ Common Issues & Fixes

### ❌ Blockchain not connecting

* Check Ganache is running
* Check RPC URL

### ❌ Unauthorized device

* Call `addDevice()` again in Remix

### ❌ Contract not found

* Redeploy after restarting Ganache

### ❌ ABI Error

* Recopy ABI from Remix

---

## 🚀 Demo Checklist (Before Presentation)

✔ Ganache running
✔ Contract deployed
✔ Device authorized
✔ main.py running
✔ Dashboard live
✔ TX visible in Ganache