"""
Registry Management Utility for SecureMedi

Manages doctors, patients, and contract registries.
"""

import json
import os
from datetime import datetime
from pathlib import Path


class RegistryManager:
    """Manages all registry files."""
    
    def __init__(self, registry_dir="registry"):
        """Initialize registry manager."""
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(exist_ok=True)
        
        self.doctors_file = self.registry_dir / "doctors.json"
        self.patients_file = self.registry_dir / "patients.json"
        self.contracts_file = self.registry_dir / "contracts.json"
    
    # ============ DOCTORS =============
    
    def add_doctor(self, wallet_address, name, specialization="", hospital=""):
        """Add a new doctor to the registry."""
        doctors_data = self._load_json(self.doctors_file)
        
        # Check if doctor already exists
        for doc in doctors_data["doctors"]:
            if doc["wallet_address"].lower() == wallet_address.lower():
                return False, "Doctor already registered"
        
        # Create new doctor entry
        new_id = f"doc_{len(doctors_data['doctors']) + 1:03d}"
        new_doctor = {
            "id": new_id,
            "name": name,
            "wallet_address": wallet_address,
            "private_key": "",
            "specialization": specialization,
            "hospital": hospital,
            "registered_on": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
            "access_key_hash": ""
        }
        
        doctors_data["doctors"].append(new_doctor)
        doctors_data["metadata"]["total_doctors"] = len(doctors_data["doctors"])
        doctors_data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        self._save_json(self.doctors_file, doctors_data)
        return True, f"Doctor {new_id} registered: {name}"
    
    def get_doctors(self):
        """Get all doctors."""
        data = self._load_json(self.doctors_file)
        return data["doctors"]
    
    def get_doctor(self, doctor_id):
        """Get a specific doctor."""
        doctors = self.get_doctors()
        for doc in doctors:
            if doc["id"] == doctor_id or doc["wallet_address"].lower() == doctor_id.lower():
                return doc
        return None
    
    def update_doctor_key(self, doctor_id, access_key_hash):
        """Update doctor's access key."""
        doctors_data = self._load_json(self.doctors_file)
        
        for doc in doctors_data["doctors"]:
            if doc["id"] == doctor_id or doc["wallet_address"].lower() == doctor_id.lower():
                doc["access_key_hash"] = access_key_hash
                self._save_json(self.doctors_file, doctors_data)
                return True
        return False
    
    # ============ PATIENTS =============
    
    def add_patient(self, patient_id, name, wallet_address, email="", dob=""):
        """Add a new patient to the registry."""
        patients_data = self._load_json(self.patients_file)
        
        # Check if patient already exists
        for pat in patients_data["patients"]:
            if pat["id"].lower() == patient_id.lower():
                return False, "Patient already registered"
        
        new_patient = {
            "id": patient_id,
            "name": name,
            "wallet_address": wallet_address,
            "private_key": "",
            "email": email,
            "date_of_birth": dob,
            "registered_on": datetime.now().strftime("%Y-%m-%d"),
            "status": "active",
            "emergency_contact": "",
            "medical_conditions": []
        }
        
        patients_data["patients"].append(new_patient)
        patients_data["metadata"]["total_patients"] = len(patients_data["patients"])
        patients_data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        self._save_json(self.patients_file, patients_data)
        return True, f"Patient {patient_id} registered: {name}"
    
    def get_patients(self):
        """Get all patients."""
        data = self._load_json(self.patients_file)
        return data["patients"]
    
    def get_patient(self, patient_id):
        """Get a specific patient."""
        patients = self.get_patients()
        for pat in patients:
            if pat["id"].lower() == patient_id.lower():
                return pat
        return None
    
    def update_patient_wallet(self, patient_id, wallet_address, private_key=""):
        """Update patient's wallet address and private key."""
        patients_data = self._load_json(self.patients_file)
        
        for pat in patients_data["patients"]:
            if pat["id"].lower() == patient_id.lower():
                pat["wallet_address"] = wallet_address
                if private_key:
                    pat["private_key"] = private_key
                self._save_json(self.patients_file, patients_data)
                return True
        return False
    
    # ============ CONTRACTS =============
    
    def add_contract(self, contract_id, contract_address, deployer, network="Ganache", 
                    chain_id=1337, rpc_url="http://127.0.0.1:7545"):
        """Add a new contract to the registry."""
        contracts_data = self._load_json(self.contracts_file)
        
        new_contract = {
            "id": contract_id,
            "name": "SecureMedi Health Logger",
            "contract_address": contract_address,
            "deployer": deployer,
            "network": network,
            "chain_id": chain_id,
            "rpc_url": rpc_url,
            "deployed_on": datetime.now().strftime("%Y-%m-%d"),
            "solidity_version": "0.8.17",
            "status": "active",
            "abi_file": "contracts/abi.json",
            "bytecode_file": "contracts/bytecode.bin"
        }
        
        contracts_data["contracts"].append(new_contract)
        contracts_data["metadata"]["total_contracts"] = len(contracts_data["contracts"])
        contracts_data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        
        self._save_json(self.contracts_file, contracts_data)
        return True, f"Contract {contract_id} registered"
    
    def get_contracts(self):
        """Get all contracts."""
        data = self._load_json(self.contracts_file)
        return data["contracts"]
    
    def get_active_contract(self):
        """Get the active contract."""
        contracts = self.get_contracts()
        for contract in contracts:
            if contract["status"] == "active":
                return contract
        return contracts[-1] if contracts else None
    
    # ============ UTILITY =============
    
    def _load_json(self, filepath):
        """Load JSON file."""
        if not filepath.exists():
            return {"data": [], "metadata": {}}
        
        with open(filepath, "r") as f:
            return json.load(f)
    
    def _save_json(self, filepath, data):
        """Save JSON file."""
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
    
    def print_summary(self):
        """Print registry summary."""
        print("\n" + "=" * 60)
        print("SECUREMEDI REGISTRY SUMMARY")
        print("=" * 60)
        
        doctors = self.get_doctors()
        patients = self.get_patients()
        contracts = self.get_contracts()
        
        print(f"\nDoctors: {len(doctors)}")
        for doc in doctors:
            print(f"  - {doc['name']} ({doc['id']})")
            print(f"    Wallet: {doc['wallet_address']}")
        
        print(f"\nPatients: {len(patients)}")
        for pat in patients:
            print(f"  - {pat['name']} ({pat['id']})")
            print(f"    Wallet: {pat['wallet_address']}")
        
        print(f"\nContracts: {len(contracts)}")
        for contract in contracts:
            print(f"  - {contract['name']} ({contract['id']})")
            print(f"    Address: {contract['contract_address']}")
            print(f"    Network: {contract['network']}")
        
        print("=" * 60 + "\n")


if __name__ == "__main__":
    # Example usage
    registry = RegistryManager()
    registry.print_summary()
