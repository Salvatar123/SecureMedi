# Security Best Practices

## Overview

This document outlines security best practices for deploying and operating SecureMedi. Given the sensitive nature of health data, security is a critical concern.

---

## Table of Contents

1. [Credential Management](#credential-management)
2. [Data Protection](#data-protection)
3. [Authentication & Authorization](#authentication--authorization)
4. [Network Security](#network-security)
5. [Blockchain Security](#blockchain-security)
6. [Code Security](#code-security)
7. [Deployment Security](#deployment-security)
8. [Incident Response](#incident-response)
9. [Security Checklist](#security-checklist)

---

## Credential Management

### Private Keys & Secrets

❌ **NEVER**:
- Hardcode private keys in source code
- Commit `.env` files to version control
- Share private keys via email or chat
- Log sensitive data
- Expose private keys in error messages

✅ **DO**:
- Store private keys in secure vaults (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
- Inject secrets at runtime via environment variables
- Use `.env.example` as a template (no real values)
- Rotate keys regularly (monthly for production)
- Audit key access logs

### Environment Variable Handling

```bash
# ✅ Correct: Load from environment at runtime
from config.settings import get_settings
settings = get_settings()  # Reads from .env at runtime

# ❌ Wrong: Hardcoded values
CONTRACT_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc8e7595f42e11"
PRIVATE_KEY = "0xabc123def456..."
```

### .gitignore Configuration

Ensure `.gitignore` includes:
```bash
# Environment variables
.env
.env.local
.env.*.local
config/.env
config/production.env

# Sensitive data
logs/data.csv
private_keys/
*.key
*.pem

# Build/dependency artifacts
__pycache__/
.pytest_cache/
*.egg-info/
dist/
build/

# IDE secrets
.vscode/launch.json
.idea/
```

---

## Data Protection

### Health Data Classification

**Public**: Application metadata, API documentation
**Internal**: Configuration, deployment details  
**Confidential**: Patient health data, access logs
**Restricted**: Private keys, user credentials

### CSV Data Protection

**File**: `logs/data.csv`

```bash
# ✅ Restrict file access (development)
chmod 600 logs/data.csv

# ✅ In Docker, use secrets:
docker run --secret db_password \
  -e PRIVATE_KEY=/run/secrets/private_key \
  securemedi:latest

# ✅ Archive old logs
mv logs/data.csv logs/data.$(date +%Y%m%d).csv.gz
```

### Encryption at Rest

```python
# Example: Encrypt sensitive CSV columns
from cryptography.fernet import Fernet

def encrypt_patient_id(patient_id: str, key: bytes) -> str:
    """Encrypt patient ID before storage."""
    f = Fernet(key)
    return f.encrypt(patient_id.encode()).decode()

def decrypt_patient_id(encrypted: str, key: bytes) -> str:
    """Decrypt patient ID from storage."""
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()
```

### Encryption in Transit

✅ **Always use HTTPS/TLS**:

```bash
# Dashboard over HTTPS with Next.js
# Use Next.js with SSL certificates or reverse proxy
# See DEPLOYMENT.md for nginx configuration with Next.js
```

---

## Authentication & Authorization

### Blockchain Access Keys

**Key Generation** (secure):
```python
from web3 import Web3

# ✅ Generate cryptographically secure keys
account = w3.eth.account.create()
private_key = account.key.hex()  # Store securely, never log
```

**Key Verification** (dashboard login):
```python
# User provides:
# 1. Wallet address (public)
# 2. Access key (secret, with password protection)

valid = blockchain_service.verify_key(wallet_address, key_bytes)
```

### Session Management

**JWT Token Management** (production):
```typescript
// Frontend - Zustand store with cookie persistence
const { token, login, logout } = useAuthStore();

// Tokens stored in httpOnly cookies (secure)
cookie.set('auth_token', token, { secure: true, sameSite: 'strict' });
```
if st.session_state.authenticated:
    # Token expires after inactivity
    if time_since_login > MAX_SESSION_AGE:
        st.session_state.authenticated = False
```

**Production Session Best Practices**:
- Use secure, HTTP-only cookies
- Implement session timeout (30 min default)
- Require CSRF tokens for state-changing operations
- Log all authentication events

### Role-Based Access Control

```python
# ✅ Implement role checks
ROLES = {
    "doctor": ["view_patient", "log_access"],
    "patient": ["view_own_data", "view_access_logs"],
    "admin": ["manage_users", "audit_logs"],
}

def require_role(required_role: str):
    """Decorator to check user role."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if st.session_state.user_role != required_role:
                st.error("Unauthorized access")
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## Network Security

### API Security

**Input Validation** (mandatory):
```python
from utils.validators import (
    validate_eth_address,
    validate_patient_id,
    validate_health_data,
)

# ✅ Always validate user input
if not validate_eth_address(user_input):
    raise ValueError("Invalid Ethereum address")
```

**Rate Limiting** (production):
```python
# Use tools like:
# - Nginx rate limiting
# - API Gateway throttling
# - Redis-based rate limiting

# Example limits:
# - Login attempts: 5 per minute
# - API calls: 100 per hour per user
# - Dashboard access: 60 requests per minute
```

### Firewall Rules

**Restrict network access**:
```bash
# Only expose necessary ports
# Dashboard: 8501 (with reverse proxy authentication)
# Blockchain: 7545 (internal only, not exposed)
# Application: (internal only, no external access)

# Example iptables (Linux):
sudo iptables -A INPUT -p tcp --dport 8501 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 7545 -j DROP
sudo iptables -A INPUT -p tcp --dport 22 -s TRUSTED_IP -j ACCEPT
```

---

## Blockchain Security

### Contract Interactions

**Gas Limit Validation**:
```python
# Prevent gas limit attacks
MAX_GAS_LIMIT = 5000000

if tx_gas_limit > MAX_GAS_LIMIT:
    raise ValueError(f"Gas limit exceeds maximum: {tx_gas_limit}")
```

**Nonce Handling**:
```python
# ✅ Prevent transaction replay attacks
nonce = w3.eth.get_transaction_count(account)
tx = contract.functions.logAccess(patient_id)\
    .build_transaction({
        "from": account,
        "nonce": nonce,  # Increment for each transaction
        "gas": GAS_LIMIT,
    })
```

### Private Key Storage

**Local Development** (Ganache):
```bash
# ✅ Use mnemonic (deterministic, test-only)
ganache-cli --mnemonic "test test test test test test test test test test test junk"

# Keys from this mnemonic are public, only for testing
```

**Production** (Testnet/Mainnet):
```bash
# ❌ Never use hardcoded keys
PRIVATE_KEY = "0xabc..."  # WRONG!

# ✅ Use secure key storage
import os
from web3 import Web3

private_key = os.getenv("PRIVATE_KEY")  # From secure vault
if not private_key:
    raise ValueError("PRIVATE_KEY not configured")

account = w3.eth.account.from_key(private_key)
```

### Smart Contract Best Practices

- Audit contract code with security firm (testnet phase)
- Use established patterns (OpenZeppelin libraries)
- Implement access controls (require statements)
- Test edge cases (0 values, max uint, overflow/underflow)
- Monitor contract events for anomalies

---

## Code Security

### Dependency Scanning

**Identify vulnerabilities**:
```bash
# Install safety (vulnerability scanner)
pip install safety

# Scan dependencies
safety check

# Generate report
safety check --json > security_report.json
```

**Lock versions** (requirements.txt):
```
pydantic==2.0.3  # ✅ Pinned version
web3==6.9.0
streamlit==1.28.1
```

### Code Quality & Static Analysis

**Type checking** (mypy):
```bash
mypy services/ utils/ main.py --strict
```

**Linting** (flake8):
```bash
flake8 . --max-line-length=100
```

**Code formatting** (black):
```bash
black .
```

### Secrets in Code Detection

**Scan for exposed secrets**:
```bash
# Install git-secrets
brew install git-secrets  # macOS
sudo apt-get install git-secrets  # Ubuntu

# Install patterns
git secrets --install

# Scan pre-commit
git secrets --pre-commit

# Scan all history
git log -p | grep -i "private\|secret\|key\|password"
```

---

## Deployment Security

### Docker Security

**Image scanning**:
```bash
# Scan for vulnerabilities
docker scan securemedi:latest

# Use minimal base image
FROM python:3.11-slim  # ✅ Smaller attack surface

# Run as non-root
RUN useradd -m -u 1000 appuser
USER appuser
```

**Docker secrets** (production):
```bash
# Use Docker secrets for sensitive data
docker secret create db_password -
docker run --secret db_password \
  -e PRIVATE_KEY=/run/secrets/db_password \
  securemedi:latest
```

### SSL/TLS Certificates

**Generate self-signed cert** (development):
```bash
openssl req -x509 -newkey rsa:4096 \
  -out cert.pem -keyout key.pem -days 365 -nodes
```

**Use Let's Encrypt** (production):
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate (Nginx)
sudo certbot certonly --nginx -d yourdomain.com
```

### Access Control

**SSH key management**:
```bash
# Generate keys
ssh-keygen -t ed25519 -C "deployments@securemedi"

# Restrict permissions
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub

# Disable password auth
ssh -o PasswordAuthentication=no user@host
```

---

## Incident Response

### Potential Incidents

1. **Private Key Exposure**
   - Immediately revoke key in blockchain
   - Generate new key from secure vault
   - Audit all transactions signed with exposed key
   - Notify affected patients

2. **Data Breach (CSV compromise)**
   - Isolate affected system
   - Notify data protection authority
   - Review access logs for suspicious activity
   - Reset all patient credentials
   - Implement enhanced monitoring

3. **Unauthorized Access**
   - Immediately disable compromised account
   - Review access logs and timeline
   - Reset session tokens
   - Implement multi-factor authentication
   - Increase monitoring

### Logging & Monitoring

**Security event logging**:
```python
import logging

security_logger = logging.getLogger("security")

# Log authentication events
security_logger.info(f"User {user_id} logged in from {ip_address}")

# Log failed attempts
security_logger.warning(f"Failed login attempt for {user_id}")

# Log access to sensitive data
security_logger.info(f"Patient data accessed by {doctor_id}")
```

**Alert Configuration**:
```bash
# Volume of failed logins > threshold
# Unusual geographic access patterns
# Blockchain transaction failures
# CSV file permission changes
# Unauthorized network connections
```

---

## Security Checklist

### Development
- [ ] No hardcoded secrets in code
- [ ] `.env` added to `.gitignore`
- [ ] Input validation on all user inputs
- [ ] Type hints for function parameters
- [ ] Error handling without leaking sensitive info
- [ ] HTTPS/TLS for all communications (staging+)
- [ ] Security headers (Content-Security-Policy, X-Frame-Options)

### Testing
- [ ] Unit tests for validators (edge cases)
- [ ] Integration tests for auth flow
- [ ] Penetration testing (staging)
- [ ] Dependency vulnerability scan (`safety check`)
- [ ] Secrets detection (`git-secrets`)
- [ ] Code review by security team

### Deployment
- [ ] Private keys in secure vault, not .env
- [ ] All environment variables documented
- [ ] Docker image scanned (`docker scan`)
- [ ] Firewall rules configured
- [ ] SSL/TLS certificates installed
- [ ] Monitoring and alerting enabled
- [ ] Log retention policy defined
- [ ] Backup strategy implemented

### Operations
- [ ] Regular security updates applied
- [ ] Key rotation schedule (monthly)
- [ ] Access logs reviewed weekly
- [ ] Incident response plan tested
- [ ] Security team on-call
- [ ] Compliance audits scheduled
- [ ] Backup/disaster recovery tested

---

## Compliance & Regulations

### HIPAA (US)
- Encrypt health data at rest and in transit
- Implement access controls and audit trails
- Document security measures
- Conduct annual risk assessments
- Implement breach notification procedures

### GDPR (EU)
- Implement right to be forgotten
- Data portability support
- Consent management
- Privacy impact assessment
- Data controller agreements

### Contact
For security concerns or incident reporting:
- **Email**: security@securemedi.dev (not included, for example)
- **GitHub Issues**: Mark as security issue
- **Responsible Disclosure**: Allow 30 days before public disclosure

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Ethereum Smart Contract Best Practices](https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/)
- [Web3.py Security](https://web3py.readthedocs.io/en/stable/security.html)

---

**Last Updated**: March 16, 2026  
**Next Review**: June 16, 2026
