#!/usr/bin/env python3
"""
Registry CLI - Command line tool to manage SecureMedi registry
"""

import sys
import json
from pathlib import Path
from .registry_manager import RegistryManager


def print_menu():
    """Print the menu."""
    print("\n" + "=" * 60)
    print("SECUREMEDI REGISTRY MANAGEMENT")
    print("=" * 60)
    print("\n1. Add Doctor")
    print("2. Add Patient")
    print("3. View Doctors")
    print("4. View Patients")
    print("5. View Contracts")
    print("6. View Full Summary")
    print("7. Export Registry (JSON)")
    print("8. Exit")
    print("\n" + "=" * 60)


def add_doctor(registry):
    """Interactive prompt to add a doctor."""
    print("\n--- Add New Doctor ---")
    name = input("Doctor name: ").strip()
    wallet = input("Wallet address (0x...): ").strip()
    spec = input("Specialization (optional): ").strip()
    hospital = input("Hospital name (optional): ").strip()
    
    success, msg = registry.add_doctor(wallet, name, spec, hospital)
    if success:
        print(f"\n[SUCCESS] {msg}")
    else:
        print(f"\n[ERROR] {msg}")


def add_patient(registry):
    """Interactive prompt to add a patient."""
    print("\n--- Add New Patient ---")
    patient_id = input("Patient ID (e.g., P001): ").strip()
    name = input("Patient name: ").strip()
    wallet = input("Wallet address (0x...): ").strip()
    email = input("Email (optional): ").strip()
    dob = input("Date of birth YYYY-MM-DD (optional): ").strip()
    
    success, msg = registry.add_patient(patient_id, name, wallet, email, dob)
    if success:
        print(f"\n[SUCCESS] {msg}")
    else:
        print(f"\n[ERROR] {msg}")


def view_doctors(registry):
    """View all doctors."""
    doctors = registry.get_doctors()
    print("\n" + "=" * 60)
    print(f"DOCTORS ({len(doctors)} total)")
    print("=" * 60)
    
    if not doctors:
        print("No doctors registered")
        return
    
    for doc in doctors:
        print(f"\nID: {doc['id']}")
        print(f"Name: {doc['name']}")
        print(f"Wallet: {doc['wallet_address']}")
        print(f"Specialization: {doc['specialization']}")
        print(f"Hospital: {doc['hospital']}")
        print(f"Status: {doc['status']}")
        print(f"Registered: {doc['registered_on']}")


def view_patients(registry):
    """View all patients."""
    patients = registry.get_patients()
    print("\n" + "=" * 60)
    print(f"PATIENTS ({len(patients)} total)")
    print("=" * 60)
    
    if not patients:
        print("No patients registered")
        return
    
    for pat in patients:
        print(f"\nID: {pat['id']}")
        print(f"Name: {pat['name']}")
        print(f"Wallet: {pat['wallet_address']}")
        print(f"Email: {pat['email'] or 'N/A'}")
        print(f"DOB: {pat['date_of_birth'] or 'N/A'}")
        print(f"Status: {pat['status']}")
        print(f"Registered: {pat['registered_on']}")


def view_contracts(registry):
    """View all contracts."""
    contracts = registry.get_contracts()
    print("\n" + "=" * 60)
    print(f"CONTRACTS ({len(contracts)} total)")
    print("=" * 60)
    
    if not contracts:
        print("No contracts registered")
        return
    
    for contract in contracts:
        print(f"\nID: {contract['id']}")
        print(f"Name: {contract['name']}")
        print(f"Address: {contract['contract_address']}")
        print(f"Deployer: {contract['deployer']}")
        print(f"Network: {contract['network']}")
        print(f"Chain ID: {contract['chain_id']}")
        print(f"RPC URL: {contract['rpc_url']}")
        print(f"Status: {contract['status']}")
        print(f"Deployed: {contract['deployed_on']}")


def export_registry(registry):
    """Export registry to JSON files."""
    export_dir = Path("registry_exports")
    export_dir.mkdir(exist_ok=True)
    
    timestamp = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
    
    doctors_file = export_dir / f"doctors_{timestamp}.json"
    patients_file = export_dir / f"patients_{timestamp}.json"
    contracts_file = export_dir / f"contracts_{timestamp}.json"
    
    # Export doctors
    doctors_data = {
        "doctors": registry.get_doctors(),
        "metadata": {"exported": True}
    }
    with open(doctors_file, "w") as f:
        json.dump(doctors_data, f, indent=2)
    
    # Export patients
    patients_data = {
        "patients": registry.get_patients(),
        "metadata": {"exported": True}
    }
    with open(patients_file, "w") as f:
        json.dump(patients_data, f, indent=2)
    
    # Export contracts
    contracts_data = {
        "contracts": registry.get_contracts(),
        "metadata": {"exported": True}
    }
    with open(contracts_file, "w") as f:
        json.dump(contracts_data, f, indent=2)
    
    print(f"\n[SUCCESS] Registry exported to {export_dir}/")
    print(f"  - {doctors_file}")
    print(f"  - {patients_file}")
    print(f"  - {contracts_file}")


def main():
    """Main CLI loop."""
    registry = RegistryManager()
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-8): ").strip()
        
        if choice == "1":
            add_doctor(registry)
        elif choice == "2":
            add_patient(registry)
        elif choice == "3":
            view_doctors(registry)
        elif choice == "4":
            view_patients(registry)
        elif choice == "5":
            view_contracts(registry)
        elif choice == "6":
            registry.print_summary()
        elif choice == "7":
            export_registry(registry)
        elif choice == "8":
            print("\nExiting...")
            break
        else:
            print("\n[ERROR] Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
