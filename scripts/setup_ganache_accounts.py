"""
Ganache Account Manager

Manages Ganache accounts for SecureMedi development.
Extracts account information from running Ganache instance.

Usage:
    python setup_ganache_accounts.py
"""

import os
import sys
from web3 import Web3
from dotenv import load_dotenv

# Load env
load_dotenv()

def get_ganache_accounts():
    """Get all accounts from running Ganache instance."""
    ganache_url = os.getenv("GANACHE_URL", "http://127.0.0.1:7545")
    
    print("=" * 70)
    print("GANACHE ACCOUNT MANAGER")
    print("=" * 70)
    print()
    
    # Connect to Ganache
    print(f"Connecting to Ganache at {ganache_url}...")
    w3 = Web3(Web3.HTTPProvider(ganache_url))
    
    if not w3.is_connected():
        print("ERROR: Cannot connect to Ganache!")
        print("\nMake sure Ganache is running:")
        print("  ganache-cli --deterministic --accounts 10 --port 7545")
        return False
    
    print("SUCCESS: Connected to Ganache!")
    print()
    
    # Get accounts
    try:
        accounts = w3.eth.accounts
        print(f"Found {len(accounts)} accounts:")
        print()
        
        for i, account in enumerate(accounts):
            balance = w3.from_wei(w3.eth.get_balance(account), "ether")
            print(f"Account {i}:")
            print(f"  Address:  {account}")
            print(f"  Balance:  {balance} ETH")
            
            if i == 0:
                print(f"  [DEFAULT ACCOUNT FOR DEPLOYMENT]")
            print()
        
        # Save default account to .env
        print("=" * 70)
        print("CONFIGURATION")
        print("=" * 70)
        print()
        
        default_account = accounts[0]
        print(f"Default Account (for deployment): {default_account}")
        print()
        
        # Get private key from environment
        private_key = os.getenv("PRIVATE_KEY")
        if private_key:
            print(f"Private Key (from .env): {private_key[:10]}...{private_key[-10:]}")
        else:
            print("WARNING: PRIVATE_KEY not set in .env")
            print("Set it to the private key of the default account")
        
        print()
        print("These accounts are managed by Ganache with the mnemonic:")
        print("  'test test test test test test test test test test test junk'")
        print()
        print("NOTE: These are test accounts with no real value!")
        print("      Never use these private keys in production!")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    success = get_ganache_accounts()
    
    if success:
        print()
        print("=" * 70)
        print("Account setup complete!")
        print("=" * 70)
        sys.exit(0)
    else:
        print()
        print("=" * 70)
        print("Account setup failed!")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
