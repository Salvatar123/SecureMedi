# SecureMedi Registry System

This directory contains the registry management system for SecureMedi.

## Files

- **doctors.json** - Registry of all registered doctors
- **patients.json** - Registry of all registered patients  
- **contracts.json** - Registry of deployed smart contracts
- **registry_manager.py** - Python utility class for managing registries

## Usage

### View Current Registry Status
```bash
python registry_manager.py
```

### Add New Doctors/Patients
Use the interactive CLI tool from the parent directory:
```bash
cd ..
python manage_registry.py
```

## Registry Structure

### Doctor Record
```json
{
  "id": "doc_001",
  "name": "Dr. John Smith",
  "wallet_address": "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1",
  "private_key": "",
  "specialization": "Cardiology",
  "hospital": "City Medical Center",
  "registered_on": "2026-03-24",
  "status": "active",
  "access_key_hash": ""
}
```

### Patient Record
```json
{
  "id": "P001",
  "name": "Jane Doe",
  "wallet_address": "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1",
  "private_key": "",
  "email": "jane@example.com",
  "date_of_birth": "1990-01-15",
  "registered_on": "2026-03-24",
  "status": "active",
  "emergency_contact": "John Doe",
  "medical_conditions": []
}
```

### Contract Record
```json
{
  "id": "SecureMedi_v1",
  "name": "SecureMedi Health Logger",
  "contract_address": "0xb09bCc172050fBd4562da8b229Cf3E45Dc3045A6",
  "deployer": "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1",
  "network": "Ganache",
  "chain_id": 1337,
  "rpc_url": "http://127.0.0.1:7545",
  "deployed_on": "2026-03-24",
  "solidity_version": "0.8.17",
  "status": "active"
}
```

## Important Notes

⚠️ **Security**: Private keys should never be committed to version control. Use `.gitignore` to exclude these files.

⚠️ **Backup**: Keep regular backups of your registry files, especially for production use.

✓ **Integration**: The deployment script automatically registers new contracts in the registry.
