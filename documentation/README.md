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

```
SecureMedi/
│
├── config/                    # Configuration management
│   ├── settings.py           # Pydantic BaseSettings
│   └── __init__.py
│
├── services/                  # Core business logic
│   ├── blockchain_service.py # Blockchain operations
│   ├── detector_service.py   # Anomaly detection
│   ├── logger_service.py     # Health data logging
│   └── __init__.py
│
├── utils/                     # Utility functions
│   ├── error_handler.py      # Error handling
│   ├── validators.py         # Input validation
│   └── __init__.py
│
├── blockchain/                # Legacy blockchain module
│   ├── connector.py          # Backward-compatibility wrapper
│   └── __pycache__/
│
├── contracts/                 # Smart contracts
│   ├── abi.json              # Contract ABI
│   └── Healthlogger.sol      # Solidity contract
│
├── dashboard/                 # Streamlit web interface
│   ├── app.py
│   └── __pycache__/
│
├── edge_ai/                   # Edge AI processing
│   ├── detector.py           # Backward-compatibility wrapper
│   ├── sensor.py             # Sensor data simulation
│   └── __pycache__/
│
├── logs/                      # Output directory
│   └── data.csv              # Health data logs
│
├── main.py                    # Main entry point
├── logger.py                  # Backward-compatibility wrapper
├── register_doctor.py         # Doctor registration script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variable template
├── .gitignore                # Git ignore rules
├── plan.md                   # Development plan
└── README.md                 # This file
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.8+
- Ganache CLI or Ganache GUI (v7+)
- pip or conda

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Salvatar123/SecureMedi.git
cd SecureMedi
```

### 2️⃣ Setup Python Environment

**Using venv:**
```bash
python -m venv venv
```

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

Copy the example environment file:
```bash
cp .env.example .env
```

Then edit `.env` with your settings:

```bash
# Required
ENVIRONMENT=development
GANACHE_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=<your-deployed-contract-address>
PRIVATE_KEY=<your-private-key>

# Optional - defaults work for development
ENABLE_BLOCKCHAIN=true
ENABLE_LOCAL_LOGGING=true
```

---

## ▶️ How to Run

### Step 1: Start Ganache (Blockchain Network)

**Option A: Using Ganache CLI**
```bash
ganache-cli --host 127.0.0.1 --port 7545
```

**Option B: Using Ganache GUI**
- Open Ganache application
- Click "Quickstart Ethereum"
- Verify RPC URL: `http://127.0.0.1:7545`

### Step 2: Deploy Smart Contract

1. Open [Remix IDE](https://remix.ethereum.org)
2. Create new file `Healthlogger.sol` and copy contract code from `contracts/Healthlogger.sol`
3. Connect to Ganache:
   - Go to Deploy tab → Environment → Custom Provider
   - Enter: `http://127.0.0.1:7545`
4. Compile contract (Solidity 0.8.17)
5. Deploy contract
6. **Save the contract address and update `.env`:**
   ```bash
   CONTRACT_ADDRESS=0x...deployed...address...
   ```
7. Copy ABI from Remix and save to `contracts/abi.json`

### Step 3: Run Main System

```bash
python main.py
```

Expected output:
```
2024-03-13 10:30:45,123 - __main__ - INFO - 🚀 secureMedi System Started...
2024-03-13 10:30:46,234 - __main__ - INFO - Vitals: {'heart': 75, 'temp': 37.2, 'spo2': 98}
2024-03-13 10:30:46,235 - __main__ - INFO - Status: NORMAL
```

To stop: Press `Ctrl + C`

### Step 4: Run Dashboard (in new terminal)

```bash
streamlit run dashboard/app.py
```

Dashboard opens at: `http://localhost:8501`

**Tabs:**
- **Login**: Verify blockchain access keys
- **Doctor Panel**: Generate keys, access patient records, emergency mode
- **Patient Portal**: View your health reports and access logs

---

## 🎬 Quick Demo

1. Start Ganache
2. Deploy smart contract and update `.env`
3. In terminal 1: `python main.py`
4. In terminal 2: `streamlit run dashboard/app.py`
5. View generated vitals in console
6. Access patient reports in dashboard
7. Check blockchain transactions in Ganache

---

## 📊 Output Files

- **`logs/data.csv`**: Health vital data with timestamps
  ```csv
  timestamp,heart,temp,spo2,status
  2024-03-13T10:30:46.234567,75,37.2,98,NORMAL
  2024-03-13T10:30:51.456789,112,38.5,91,ALERT
  ```

- **Blockchain Logs**: Transaction hashes for ALERT events stored on-chain

---

## 🔧 Architecture & Services

### Service Layer

New code uses a **service-oriented architecture** for easier testing and deployment:

```python
# New approach (recommended)
from services.blockchain_service import BlockchainService
from services.detector_service import DetectorService
from services.logger_service import LoggerService

blockchain = BlockchainService()
detector = DetectorService()
logger = LoggerService()
```

### Configuration Management

All settings are managed via environment variables using Pydantic:

```python
from config.settings import get_settings

settings = get_settings()
print(settings.HEART_RATE_MAX)  # Read from .env
```

### Validation

Input validation is centralized in `utils/validators.py`:

```python
from utils.validators import (
    validate_eth_address,
    validate_patient_id,
    validate_private_key,
    validate_health_data
)

if validate_eth_address(user_input):
    # Safe to use
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=services --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_detector_service.py -v
```

---

## 📋 Configuration Reference

Key environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | development | Environment (development/staging/production) |
| `GANACHE_URL` | http://127.0.0.1:7545 | Blockchain RPC endpoint |
| `CONTRACT_ADDRESS` | (required) | Deployed smart contract address |
| `PRIVATE_KEY` | (required) | Account private key for transactions |
| `HEART_RATE_MAX` | 110 | Anomaly detection threshold (bpm) |
| `TEMPERATURE_MAX` | 38.0 | Anomaly detection threshold (°C) |
| `SPO2_MIN` | 92 | Anomaly detection threshold (%) |
| `LOG_FILE` | logs/data.csv | Path to health data CSV |
| `ENABLE_BLOCKCHAIN` | true | Enable blockchain operations |
| `ENABLE_LOCAL_LOGGING` | true | Enable CSV logging |

See `.env.example` for all options.

---

## 🔮 Future Scope

- Integration with real IoT medical devices
- Cloud-based deployment
- Mobile application
- Advanced machine learning models
- Multi-hospital network
- Public blockchain integration

### 📈 Impact

secureMedi enables:

- Faster emergency response
- Improved data security
- Enhanced patient trust
- Transparent medical systems
- Scalable healthcare infrastructure

---

## 📖 Code Documentation

All public functions and classes include comprehensive docstrings in **Google/NumPy style**.

### Module Structure

Each module includes:
- Module-level docstring with purpose and usage
- Class docstrings describing responsibility
- Function docstrings with Args, Returns, Raises sections
- Type hints on all function signatures

### Example Docstring

```python
def detect(self, data: Dict[str, Any]) -> Literal["ALERT", "NORMAL"]:
    """
    Detect anomalies in health vitals.

    Args:
        data: Dictionary with heart, temp, spo2 values

    Returns:
        "ALERT" if any vital is abnormal, "NORMAL" otherwise
        
    Raises:
        DetectorException: If data validation fails
    """
    # Implementation...
```

### Documentation Files

- **[DEPLOYMENT.md](DEPLOYMENT.md)** — Cloud deployment, Docker, Kubernetes
- **[SECURITY.md](SECURITY.md)** — Security best practices, threat mitigation
- **[PHASE2_SUMMARY.md](PHASE2_SUMMARY.md)** — Test coverage and validation tasks
- **[PHASE3_SUMMARY.md](PHASE3_SUMMARY.md)** — Security fixes and code quality

---

## 🎯 Code Quality Standards

This project follows best practices for production code:

### Type Hints
- All functions have complete type hints
- Validated with `mypy . --strict` (zero errors)

### Code Formatting
- Formatted with `black` (88-character line length)
- Linted with `flake8` (zero violations)

### Testing
- Unit tests in `tests/` directory
- 126 tests across all services and utilities
- 70%+ code coverage via `pytest --cov`
- Test fixtures for all services in `tests/conftest.py`

### Code Organization
- **services/**: Core business logic (blockchain, logging, detection)
- **utils/**: Reusable utilities (validators, error handling)
- **config/**: Configuration management via environment variables
- **tests/**: Comprehensive test suite with fixtures

---

## 🔐 Security

For security best practices, threat modeling, and incident response procedures, see [SECURITY.md](SECURITY.md).

Key security features:
- ✅ No hardcoded credentials in source code
- ✅ Environment-based configuration
- ✅ Input validation on all user inputs
- ✅ Thread-safe operations
- ✅ Comprehensive secrets in `.gitignore`
- ✅ Session-based authentication for dashboard

---

## 🚀 Deployment

For detailed deployment instructions for local, staging, and production environments, see [DEPLOYMENT.md](DEPLOYMENT.md).

Quick deployment options:
- **Local**: `python main.py` + `streamlit run dashboard/app.py`
- **Docker**: `docker build -t securemedi:latest . && docker run securemedi:latest`
- **Docker Compose**: `docker-compose up -d` (includes Ganache + app + dashboard)
