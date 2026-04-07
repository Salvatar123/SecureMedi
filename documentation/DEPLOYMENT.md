# Deployment Guide

## Overview

This guide covers deploying SecureMedi to production environments. SecureMedi is a health monitoring system with blockchain integration for secure access logging.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Blockchain Configuration](#blockchain-configuration)
6. [Monitoring & Health Checks](#monitoring--health-checks)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Python 3.8+** (tested with 3.10, 3.11)
- **Docker** 20.10+ (for containerized deployment)
- **Git** for version control
- **4GB RAM** minimum
- **2GB disk space** for logs and data

### External Services
- **Blockchain Node** (Ganache for development, testnet/mainnet for production)
- **Ethereum Wallet** with sufficient funds for gas fees (production)

### Development Tools (Optional)
- **Docker Compose** for multi-container orchestration
- **Next.js** for modern dashboard deployment
- **Nginx/HAProxy** for load balancing (production)

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/your-org/securemedi.git
cd securemedi
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Using conda
conda create -n securemedi python=3.11
conda activate securemedi
```

### 3. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your local settings
nano .env
```

### 5. Start Ganache (Local Blockchain)

```bash
# Using ganache-cli
ganache-cli --deterministic --accounts=10

# Or using ganache GUI
# Download from: https://trufflesuite.com/ganache/
```

### 6. Run Application

```bash
# Main monitoring system
python main.py

# Dashboard (v2.0 - Next.js) in separate terminals:

# Terminal 2: Backend API
cd backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 3: Frontend
cd frontend
npm install
npm run dev  # Opens http://localhost:3000
```

---

## Docker Deployment

### Prerequisites
- Docker installed and running
- Docker Compose installed (for multi-container setup)

### Single Container Deployment

#### 1. Build Image

```bash
docker build -t securemedi:latest .
```

#### 2. Run Container

```bash
docker run -d \
  --name securemedi-backend \
  -e GANACHE_URL=http://ganache:7545 \
  -e CONTRACT_ADDRESS=0x... \
  -e PRIVATE_KEY=0x... \
  -v $(pwd)/logs:/app/logs \
  -p 8000:8000 \
  securemedi-backend:latest
```

### Multi-Container Deployment with Docker Compose

#### 1. Start Services

```bash
docker-compose up -d
```

This starts:
- **backend**: FastAPI server (port 8000)
- **frontend**: Next.js React app (port 3000)
- **ganache**: Local blockchain (port 7545)

#### 2. Stop Services

```bash
docker-compose down
```

#### 3. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f securemedi
```

---

## Environment Configuration

### Configuration Files

- `.env` — Local environment variables
- `.env.development` — Development environment template
- `.env.staging` — Staging environment template
- `.env.production` — Production environment template

### Required Variables

```bash
# Blockchain Configuration
GANACHE_URL=http://127.0.0.1:7545
CONTRACT_ADDRESS=0x...  # Deployed contract address
PRIVATE_KEY=0x...       # Private key (KEEP SECURE!)

# Application Settings
ENVIRONMENT=development  # or staging, production
DEFAULT_PATIENT_ID=P001
ENABLE_BLOCKCHAIN=false  # Set to true for blockchain integration
ENABLE_LOCAL_LOGGING=true

# Logging
LOG_FILE=logs/data.csv
LOG_LEVEL=INFO

# Detector Thresholds (configurable at runtime)
HEART_RATE_MAX=110
TEMPERATURE_MAX=38.0
SPO2_MIN=92

# Sensor Settings
SENSOR_INTERVAL_SEC=5
```

### Environment-Specific Examples

#### Development (.env.development)
```bash
ENVIRONMENT=development
ENABLE_BLOCKCHAIN=false
LOG_LEVEL=DEBUG
SENSOR_INTERVAL_SEC=5
```

#### Production (.env.production)
```bash
ENVIRONMENT=production
ENABLE_BLOCKCHAIN=true
LOG_LEVEL=INFO
SENSOR_INTERVAL_SEC=60
```

---

## Blockchain Configuration

### Local Development (Ganache)

1. Start Ganache:
   ```bash
   ganache-cli --deterministic --accounts=10
   ```

2. Deploy contract:
   ```bash
   # Using Truffle (if available)
   truffle migrate --network ganache
   
   # Or manually deploy and update CONTRACT_ADDRESS in .env
   ```

3. Set environment variables:
   ```bash
   GANACHE_URL=http://127.0.0.1:7545
   CONTRACT_ADDRESS=0x...
   PRIVATE_KEY=0x...  # From Ganache accounts
   ```

### Testnet Deployment (Sepolia/Goerli)

1. Get testnet ETH from faucet:
   - Sepolia: https://sepoliafaucet.com
   - Goerli: https://goerlifaucet.com

2. Deploy contract to testnet:
   ```bash
   truffle migrate --network sepolia
   ```

3. Update environment variables:
   ```bash
   GANACHE_URL=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
   CONTRACT_ADDRESS=0x...
   PRIVATE_KEY=0x...  # Your testnet wallet key
   ```

### Mainnet Deployment (Production)

⚠️ **CRITICAL SECURITY**: Never expose private keys in version control.

1. Generate secure wallet:
   ```bash
   # Using web3.py
   from web3 import Web3
   w3 = Web3()
   acct = w3.eth.account.create()
   print(f"Address: {acct.address}")
   print(f"Key: {acct.key.hex()}")
   ```

2. Fund account with ETH (mainnet)

3. Deploy contract:
   ```bash
   truffle migrate --network mainnet
   ```

4. Store private key securely:
   - Use AWS Secrets Manager, Azure Key Vault, etc.
   - Inject at runtime via environment variables
   - Never commit to repository

5. Configure environment:
   ```bash
   GANACHE_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
   CONTRACT_ADDRESS=0x...
   PRIVATE_KEY=<retrieved from secure vault>
   ```

---

## Monitoring & Health Checks

### Application Logs

View logs:
```bash
# Local logs (development)
tail -f logs/data.csv

# Docker logs
docker logs -f securemedi

# Filtered logs
grep "ALERT" logs/data.csv
```

### Health Status

Check if services are running:
```bash
# Blockchain connection
curl http://localhost:7545

# Dashboard (Streamlit)
curl http://localhost:8501

# Application status
ps aux | grep main.py
```

### CSV Data Validation

```bash
# View latest records
tail -10 logs/data.csv

# Count records
wc -l logs/data.csv

# Check for alerts
grep "ALERT" logs/data.csv | wc -l
```

### Performance Monitoring

Track key metrics:
- **Sensor collection rate** — should match SENSOR_INTERVAL_SEC
- **Alert frequency** — % of records with ALERT status
- **Blockchain latency** — time to log transactions (if enabled)
- **CSV write latency** — time to save log entries

---

## Troubleshooting

### Connection Errors

**Error**: `Cannot connect to blockchain at http://127.0.0.1:7545`

**Solutions**:
- Ensure Ganache is running: `ganache-cli --deterministic`
- Check GANACHE_URL in .env matches actual address
- Verify firewall allows connection to port 7545
- Check network connectivity

### Configuration Errors

**Error**: `KeyError: 'CONTRACT_ADDRESS'`

**Solutions**:
- Ensure .env file exists in project root
- Verify CONTRACT_ADDRESS is set: `echo $CONTRACT_ADDRESS`
- Check .env syntax (no quotes around values needed)
- Reload environment: `source .env`

### Permission Errors

**Error**: `PermissionError: logs/data.csv`

**Solutions**:
- Check log directory exists: `mkdir -p logs`
- Fix permissions: `chmod 755 logs`
- Ensure write access: `touch logs/data.csv`

### Docker Build Errors

**Error**: `No module named 'services'`

**Solutions**:
- Verify WORKDIR in Dockerfile is `/app`
- Check COPY commands include all directories
- Rebuild image: `docker build --no-cache -t securemedi:latest .`

### Memory Issues

**Error**: `MemoryError` or OOM killed

**Solutions**:
- Increase Docker memory: `docker run -m 4g ...`
- Archive old logs: `mv logs/data.csv logs/data.backup.csv`
- Check CSV file size: `du -sh logs/data.csv`
- Implement log rotation in production

### Blockchain Transaction Failures

**Error**: `Gas estimation failed`

**Solutions**:
- Increase GAS_LIMIT in .env: `GAS_LIMIT=5000000`
- Check account balance: has enough ETH for gas fees
- Verify CONTRACT_ADDRESS is correct
- Check smart contract is deployed: `web3.eth.get_code(contract_address)`

---

## Security Checklist

- [ ] `.env` is in `.gitignore` and never committed
- [ ] Private keys stored securely (never hardcoded)
- [ ] HTTPS/TLS enabled for API communications
- [ ] Regular security updates: `pip install --upgrade -r requirements.txt`
- [ ] Monitor logs for suspicious activity
- [ ] Implement rate limiting for dashboard access
- [ ] Use VPN for remote connections
- [ ] Enable Docker security scanning: `docker scan securemedi:latest`

---

## Performance Optimization

### For High-Volume Data

1. **Batch CSV writes** — if collecting >1000 samples/minute
2. **Archive logs** — rotate data.csv weekly
3. **Use database** — migrate from CSV to PostgreSQL/MongoDB for scale
4. **Implement caching** — for dashboard access logs

### For Multiple Patients

1. **Horizontal scaling** — run multiple instances with load balancer
2. **Message queue** — use RabbitMQ/Kafka for high-throughput
3. **Separate blockchain** — reduce write frequency, batch transactions

---

## Support & Updates

- **GitHub Issues**: https://github.com/your-org/securemedi/issues
- **Documentation**: See README.md
- **Security Concerns**: See SECURITY.md

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] .env file created from .env.example
- [ ] Blockchain node operational
- [ ] Smart contract deployed
- [ ] Logs directory writable
- [ ] Dependencies installed
- [ ] Application tested locally
- [ ] Docker image built successfully
- [ ] Container health checks passing
- [ ] Monitoring/alerting configured
