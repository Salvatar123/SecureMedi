"""
Smart Contract Compiler and Deployer for SecureMedi

This script compiles the Solidity contract and deploys it to Ganache.
It then updates .env with the deployed contract address and registers it in the registry.

Usage:
    python compile_and_deploy.py
"""

import subprocess
import sys
import os
import json
from web3 import Web3
from dotenv import load_dotenv

# Import registry manager
sys.path.insert(0, os.path.dirname(__file__))
try:
    from registry.registry_manager import RegistryManager
except ImportError:
    RegistryManager = None

# Load env
load_dotenv()

def install_solc():
    """Install solc compiler."""
    print("Installing Solidity compiler...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "py-solc-x", "-q"])
        print("Solidity compiler installed!")
        return True
    except Exception as e:
        print(f"Error installing solc: {e}")
        return False

def compile_contract():
    """Compile Solidity contract."""
    try:
        from solcx import compile_files, install_solc
        import solcx
        
        print("Ensuring Solidity compiler is available...")
        try:
            # Try to install solc 0.8.17 (matching pragma in contract)
            install_solc("v0.8.17", show_progress=False)
            solcx.set_solc_version("v0.8.17")
        except Exception as e:
            print(f"Note: {e}")
            # Try with any available version
            print("Using default available Solidity version...")
        
        print("Compiling contract...")
        compiled = compile_files(
            "contracts/Healthlogger.sol",
            output_values=["abi", "bin"]
        )
        
        # Extract contract
        contract_key = "contracts/Healthlogger.sol:SecureMedi"
        if contract_key in compiled:
            contract = compiled[contract_key]
            print("Contract compiled successfully!")
            return {
                "abi": contract.get("abi"),
                "bytecode": contract.get("bin")
            }
        else:
            print(f"Contract not found. Available keys: {list(compiled.keys())}")
            return None
            
    except Exception as e:
        print(f"Compilation error: {e}")
        import traceback
        traceback.print_exc()
        return None

def deploy_contract():
    """Deploy compiled contract to Ganache."""
    print("\n" + "=" * 60)
    print("Compiling and Deploying SecureMedi Contract")
    print("=" * 60 + "\n")
    
    # Step 1: Install solc if needed
    try:
        from solcx import compile_files
    except ImportError:
        if not install_solc():
            print("Failed to install solc compiler")
            return False
    
    # Step 2: Compile contract
    compiled = compile_contract()
    if not compiled or not compiled.get("bytecode"):
        print("Failed to compile contract")
        return False
    
    bytecode = compiled["bytecode"]
    abi = compiled["abi"]
    
    print(f"Bytecode length: {len(bytecode)} characters")
    
    # Step 3: Connect to Ganache
    GANACHE_URL = os.getenv("GANACHE_URL", "http://127.0.0.1:7545")
    print(f"\nConnecting to Ganache at {GANACHE_URL}...")
    
    w3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    
    if not w3.is_connected():
        print(f"ERROR: Cannot connect to Ganache")
        print("Make sure ganache-cli is running:")
        print("  ganache-cli --deterministic --accounts 10 --port 7545")
        return False
    
    print("Connected!")
    
    # Step 4: Get deployer account
    try:
        accounts = w3.eth.accounts
        deployer = accounts[0]
        print(f"\nDeploying account: {deployer}")
        balance = w3.from_wei(w3.eth.get_balance(deployer), "ether")
        print(f"Account balance: {balance} ETH")
    except Exception as e:
        print(f"Error getting accounts: {e}")
        return False
    
    # Step 5: Create contract and deploy
    try:
        print("\nDeploying contract...")
        
        SecureMedi = w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Build transaction
        tx = SecureMedi.constructor().build_transaction({
            "from": deployer,
            "gas": 3000000,
            "gasPrice": w3.to_wei(20, "gwei"),
            "nonce": w3.eth.get_transaction_count(deployer),
        })
        
        # Send transaction (Ganache will auto-sign)
        tx_hash = w3.eth.send_transaction(tx)
        print(f"Transaction sent: {tx_hash.hex()}")
        
        # Wait for receipt
        print("Waiting for deployment...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt["status"] == 1:
            contract_address = receipt["contractAddress"]
            print(f"\nSUCCESS! Contract deployed!")
            print(f"Contract Address: {contract_address}")
            
            # Step 6: Update .env (CLEAR OLD ADDRESS FIRST)
            print("\nUpdating .env...")
            update_env_file(contract_address)
            
            # Step 6b: Register in registry
            print("Registering contract in registry...")
            if RegistryManager:
                register_contract_in_registry(contract_address, deployer)
            
            # Step 7: Register deployer as doctor
            print("\nStep 7: Registering deployer as doctor...")
            if not register_deployer_as_doctor(w3, contract_address, deployer, abi):
                print("ERROR: Could not register deployer as doctor")
                return False
            print("[DONE] Step 7 complete")
            
            # Step 8: Register default test patient
            print("\nStep 8: Registering default test patient...")
            if not register_test_patient(w3, contract_address, deployer, abi):
                print("ERROR: Could not register test patient")
                return False
            print("[DONE] Step 8 complete")
            
            # Step 9: Generate access key for doctor
            print("\nStep 9: Generating access key for doctor...")
            if not generate_doctor_access_key(w3, contract_address, deployer, abi):
                print("ERROR: Could not generate access key")
                return False
            print("[DONE] Step 9 complete")
            
            return True
        else:
            print("ERROR: Deployment transaction failed!")
            return False
            
    except Exception as e:
        print(f"Deployment error: {e}")
        import traceback
        traceback.print_exc()
        return False

def update_env_file(contract_address):
    """Update .env with deployed contract address."""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        print(f"ERROR: {env_file} not found!")
        return
    
    # Read current content
    with open(env_file, "r") as f:
        content = f.read()
    
    # Use regex to replace or add CONTRACT_ADDRESS
    import re
    pattern = r'CONTRACT_ADDRESS=0x[a-fA-F0-9]*'
    
    if re.search(pattern, content):
        # Replace existing
        content = re.sub(pattern, f'CONTRACT_ADDRESS={contract_address}', content)
    else:
        # Add new line before PRIVATE_KEY
        content = content.replace('# PRIVATE_KEY not needed', f'CONTRACT_ADDRESS={contract_address}\n\n# PRIVATE_KEY not needed')
    
    # Write back
    with open(env_file, "w") as f:
        f.write(content)
    
    print(f"[OK] Updated .env: CONTRACT_ADDRESS={contract_address}")

def register_contract_in_registry(contract_address, deployer):
    """Register deployed contract in the registry."""
    try:
        registry = RegistryManager()
        success, msg = registry.add_contract(
            contract_id="SecureMedi_v1",
            contract_address=contract_address,
            deployer=deployer
        )
        if success:
            print(f"[OK] {msg}")
        else:
            print(f"[WARNING] {msg}")
    except Exception as e:
        print(f"[WARNING] Could not register contract: {e}")


def register_deployer_as_doctor(w3, contract_address, deployer, abi):
    """Register the deployer account as a doctor on the contract."""
    try:
        # Create contract instance
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Call registerDoctor function
        tx = contract.functions.registerDoctor(deployer).transact({"from": deployer})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        
        if receipt["status"] == 1:
            print(f"  [OK] Doctor registered: {deployer}")
            return True
        else:
            print(f"  [FAILED] Registration transaction failed")
            return False
    except Exception as e:
        print(f"  [ERROR] Error registering doctor: {e}")
        return False

def register_test_patient(w3, contract_address, deployer, abi):
    """Register a default test patient."""
    try:
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Use deployer as the test patient's wallet
        patient_id = "P001"
        print(f"  >> Registering patient {patient_id}...")
        print(f"  >> Contract: {contract_address}")
        print(f"  >> Deployer: {deployer}")
        
        tx = contract.functions.registerPatient(patient_id, deployer).transact({"from": deployer})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        
        if receipt["status"] == 1:
            print(f"  [OK] Test patient registered: {patient_id}")
            # Verify registration
            try:
                logs = contract.functions.getAccessLogs(patient_id).call()
                print(f"  [OK] Patient verified on contract")
            except:
                pass
            return True
        else:
            print(f"  [FAILED] Patient registration failed (status: {receipt['status']})")
            return False
    except Exception as e:
        print(f"  [ERROR] Error registering patient: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_doctor_access_key(w3, contract_address, deployer, abi):
    """Generate an access key for the doctor."""
    try:
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Call generateKey function
        tx = contract.functions.generateKey().transact({"from": deployer})
        receipt = w3.eth.wait_for_transaction_receipt(tx)
        
        if receipt["status"] == 1:
            print(f"  [OK] Access key generated for doctor")
            return True
        else:
            print(f"  [FAILED] Key generation failed")
            return False
    except Exception as e:
        print(f"  [ERROR] Error generating access key: {e}")
        return False



if __name__ == "__main__":
    success = deploy_contract()
    
    if success:
        print("\n" + "=" * 60)
        print("DEPLOYMENT COMPLETE!")
        print("=" * 60)
        print("\nNow you can run:")
        print("  python main.py")
        print("\nThe application will use blockchain for alerts!")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("DEPLOYMENT FAILED")
        print("=" * 60)
        sys.exit(1)
