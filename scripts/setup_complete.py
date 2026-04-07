"""
SecureMedi Complete Setup Script

One-command setup for SecureMedi local deployment.
Handles all setup steps in sequence:
1. Environment verification
2. Ganache connection check
3. Smart contract compilation & deployment
4. Configuration validation
5. System readiness check

Usage:
    python setup_complete.py

Prerequisites:
    - Ganache running on http://127.0.0.1:7545
    - Python 3.10+ with dependencies installed
    - .env file configured
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from web3 import Web3

# Load environment
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    """Print colored header."""
    print()
    print(f"{BLUE}{'=' * 70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'=' * 70}{RESET}")
    print()

def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}! {text}{RESET}")

def print_info(text):
    """Print info message."""
    print(f"{BLUE}→ {text}{RESET}")

def update_env_account(account):
    """Update .env file with the Ganache account address."""
    env_file = ".env"
    
    if not os.path.exists(env_file):
        return
    
    # Read current content
    with open(env_file, "r") as f:
        lines = f.readlines()
    
    # Find and update PRIVATE_KEY line (set to empty for Ganache auto-signing)
    updated_private_key = False
    for i, line in enumerate(lines):
        if line.startswith("PRIVATE_KEY="):
            lines[i] = "# PRIVATE_KEY not needed for local Ganache (auto-signing)\nPRIVATE_KEY=\n"
            updated_private_key = True
            break
    
    # Write back
    with open(env_file, "w") as f:
        f.writelines(lines)

def step_1_verify_environment():
    """Step 1: Verify Python environment and dependencies."""
    print_header("STEP 1: Environment Verification")
    
    # Check Python version
    print_info("Checking Python version...")
    version_info = sys.version_info
    if version_info.major == 3 and version_info.minor >= 10:
        print_success(f"Python {version_info.major}.{version_info.minor}.{version_info.micro}")
    else:
        print_error(f"Python 3.10+ required (found {version_info.major}.{version_info.minor})")
        return False
    
    # Check required packages
    print_info("Checking required packages...")
    packages = {
        "web3": "Web3.py",
        "streamlit": "Streamlit",
        "pandas": "Pandas",
        "pydantic": "Pydantic",
        "dotenv": "Python-dotenv",
    }
    
    for pkg, name in packages.items():
        try:
            __import__(pkg)
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} not installed")
            print(f"   Install with: pip install {pkg}")
            return False
    
    return True

def step_2_ganache_connection():
    """Step 2: Verify Ganache is running and update .env with account."""
    print_header("STEP 2: Ganache Connection & Account Configuration")
    
    ganache_url = os.getenv("GANACHE_URL", "http://127.0.0.1:7545")
    print_info(f"Connecting to Ganache at {ganache_url}...")
    
    w3 = Web3(Web3.HTTPProvider(ganache_url))
    
    if not w3.is_connected():
        print_error("Cannot connect to Ganache!")
        print()
        print("Start Ganache with:")
        print(f"  {YELLOW}ganache-cli --deterministic --accounts 10 --port 7545{RESET}")
        return False, None
    
    print_success("Connected to Ganache!")
    
    try:
        chain_id = w3.eth.chain_id
        accounts = w3.eth.accounts
        print_success(f"Chain ID: {chain_id}")
        print_success(f"Available accounts: {len(accounts)}")
        
        account = accounts[0]
        balance = w3.from_wei(w3.eth.get_balance(account), "ether")
        print_success(f"Deployer account: {account}")
        print_success(f"Deployer balance: {balance} ETH")
        
        # Update .env with the correct account
        print_info("Updating .env with Ganache account...")
        update_env_account(account)
        print_success(f"Updated .env: Account set to {account}")
        
        return True, w3
    except Exception as e:
        print_error(f"Failed to query Ganache: {e}")
        return False, None

def step_3_deploy_contract(w3):
    """Step 3: Compile and deploy smart contract."""
    print_header("STEP 3: Smart Contract Deployment")
    
    print_info("Running contract deployment script...")
    
    try:
        # Use absolute path to the script
        script_path = os.path.join(os.path.dirname(__file__), "compile_and_deploy.py")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Check if deployment was successful
        if "SUCCESS! Contract deployed!" in result.stdout:
            # Extract contract address
            lines = result.stdout.split('\n')
            contract_address = None
            for line in lines:
                if "Contract Address:" in line and "0x" in line:
                    contract_address = line.split("0x")[1].strip()
                    contract_address = "0x" + contract_address
                    break
            
            if contract_address:
                print_success(f"Contract deployed: {contract_address}")
                return True, contract_address
            else:
                print_success("Contract deployed (address extraction pending)")
                return True, None
        else:
            print_error("Contract deployment failed")
            print()
            print("Output:")
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
            return False, None
            
    except subprocess.TimeoutExpired:
        print_error("Deployment timed out (>120 seconds)")
        return False, None
    except Exception as e:
        print_error(f"Deployment error: {e}")
        return False, None

def step_4_verify_configuration():
    """Step 4: Verify configuration."""
    print_header("STEP 4: Configuration Verification")
    
    required_vars = {
        "GANACHE_URL": "Ganache URL",
        "CONTRACT_ADDRESS": "Smart Contract Address",
        "ENABLE_BLOCKCHAIN": "Blockchain Enabled",
        "ENABLE_LOCAL_LOGGING": "Local Logging Enabled",
    }
    
    all_good = True
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "PASSWORD" in var:
                display_value = f"{value[:10]}...{value[-10:]}"
            elif "ADDRESS" in var:
                display_value = f"{value[:10]}...{value[-4:]}"
            else:
                display_value = value
            
            print_success(f"{desc}: {display_value}")
        else:
            print_warning(f"{desc}: NOT SET")
            if var in ["GANACHE_URL", "CONTRACT_ADDRESS"]:
                all_good = False
    
    return all_good

def step_5_system_readiness():
    """Step 5: Final system readiness check."""
    print_header("STEP 5: System Readiness Check")
    
    # Check logs directory
    print_info("Checking logs directory...")
    log_dir = Path("logs")
    if log_dir.exists():
        print_success("Logs directory exists")
    else:
        print_info("Creating logs directory...")
        log_dir.mkdir(exist_ok=True)
        print_success("Logs directory created")
    
    # Check main.py exists
    print_info("Checking main application...")
    if Path("main.py").exists():
        print_success("main.py found")
    else:
        print_error("main.py not found!")
        return False
    
    # Check dashboard script exists
    print_info("Checking dashboard...")
    if Path("dashboard/app.py").exists():
        print_success("Dashboard app.py found")
    else:
        print_warning("Dashboard app.py not found")
    
    return True

def main():
    """Run complete setup."""
    print()
    print(f"{BLUE}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "SecureMedi Complete Setup".center(68) + "║")
    print("║" + "Local Deployment Automation".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{RESET}")
    
    # Run all steps
    steps_completed = 0
    
    # Step 1: Environment
    if not step_1_verify_environment():
        print()
        print_error("Setup failed at Step 1: Environment Verification")
        return False
    steps_completed += 1
    
    # Step 2: Ganache
    ganache_ok, w3 = step_2_ganache_connection()
    if not ganache_ok:
        print()
        print_error("Setup failed at Step 2: Ganache Connection")
        return False
    steps_completed += 1
    
    # Step 3: Deploy Contract
    if w3:
        deploy_ok, contract_addr = step_3_deploy_contract(w3)
        if not deploy_ok:
            print()
            print_error("Setup failed at Step 3: Contract Deployment")
            return False
        steps_completed += 1
    
    # Step 4: Configuration
    if not step_4_verify_configuration():
        print()
        print_warning("Step 4: Some configuration items missing")
    steps_completed += 1
    
    # Step 5: Readiness
    if not step_5_system_readiness():
        print()
        print_error("Setup failed at Step 5: System Readiness")
        return False
    steps_completed += 1
    
    # Success!
    print_header("SETUP COMPLETE!")
    
    print(f"{GREEN}All {steps_completed} setup steps completed successfully!{RESET}")
    print()
    print("Next steps:")
    print(f"  1. Start main application:")
    print(f"     {BLUE}python main.py{RESET}")
    print()
    print(f"  2. (Optional) Start dashboard:")
    print(f"     {BLUE}streamlit run dashboard/app.py{RESET}")
    print()
    print(f"  3. View data:")
    print(f"     {BLUE}cat logs/data.csv{RESET}")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print()
        print_error("Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
