# 🏥 secureMedi

**Blockchain + Edge Intelligence for Secure Healthcare Monitoring**

secureMedi is a smart healthcare monitoring system that integrates **Edge AI** and **Blockchain** to provide secure, real-time patient health tracking and tamper-proof medical records.

This project was developed as a prototype for ideathons/hackathons and academic research.

---

## 🚀 Features

- ✅ Real-time patient vital monitoring
- ✅ Edge-based anomaly detection
- ✅ Blockchain-secured medical records
- ✅ Device authorization system
- ✅ Live data visualization dashboard
- ✅ Low-latency alert mechanism
- ✅ Tamper-proof health logs

---

## 🧠 Problem Statement

Traditional healthcare monitoring systems face major challenges:

- Data tampering risks
- High cloud processing latency
- Privacy and security issues
- Lack of transparency
- Delayed emergency response

These limitations reduce trust and efficiency in healthcare systems.

---

## 💡 Solution Overview

secureMedi processes patient vitals locally using Edge AI to reduce latency and protect privacy.  
Critical alerts and medical records are stored on blockchain, ensuring immutability and transparency.

### System Architecture

Sensors → Edge AI → Blockchain → Dashboard


---

## 🛠 Technology Stack

| Layer        | Technology            |
|--------------|------------------------|
| Edge AI      | Python                 |
| Blockchain   | Solidity, Ganache      |
| Integration  | Web3.py                |
| Dashboard    | Streamlit              |
| Backend      | Python                 |

---

## 📁 Project Structure

SecureMedi/
│
├── blockchain/
│ └── connector.py
├── contracts/
│ └── abi.json
├── dashboard/
│ └── app.py
├── edge_ai/
├── logs/
├── main.py
├── requirements.txt
└── README.md


---

## ⚙️ Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Salvatar123/SecureMedi.git
cd SecureMedi

2️⃣ Install Dependencies

pip install -r requirements.txt

▶️ How to Run the Project
Step 1: Start Ganache (Blockchain Network)

Open Ganache

Click Quickstart Ethereum

Keep it running

Confirm RPC URL:

http://127.0.0.1:7545

Step 2: Deploy Smart Contract (Using Remix)

This step must be repeated whenever Ganache is restarted.

Open https://remix.ethereum.org

Connect Environment → Custom Provider

Enter:

http://127.0.0.1:7545


Compile contract (Solidity 0.8.17, EVM: Istanbul)

Deploy contract

Copy:

Contract Address

ABI

Save ABI in:

contracts/abi.json


Update contract address in:

blockchain/connector.py


Authorize device:

addDevice(your_account_address)

Step 3: Run Main System

In project root:

python main.py


Expected output:

secureMedi System Started...
Vitals: {...}
Status: NORMAL / ALERT

Step 4: Run Dashboard

Open a new terminal:

streamlit run dashboard/app.py


Dashboard will open in browser.

🎬 Demo Flow (Recommended)

Start Ganache

Deploy smart contract

Run main.py

Run dashboard

Trigger alert

Show transaction in Ganache

Stop using Ctrl + C

📊 Output

The system provides:

Live vital statistics

Alert notifications

Blockchain transaction hashes

Interactive dashboard graphs

Secure medical record storage

🔮 Future Scope

Integration with real IoT medical devices

Cloud-based deployment

Mobile application

Advanced machine learning models

Multi-hospital network

Public blockchain integration

📈 Impact

secureMedi enables:

Faster emergency response

Improved data security

Enhanced patient trust

Transparent medical systems

Scalable healthcare infrastructure