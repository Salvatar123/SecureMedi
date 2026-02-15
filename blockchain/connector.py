from web3 import Web3
import json
import os


# =====================================
# CONNECT TO GANACHE
# =====================================

GANACHE_URL = "http://127.0.0.1:7545"

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    raise Exception("❌ Ganache not connected")


# =====================================
# ACCOUNT (USE DEFAULT FUNDED)
# =====================================

ACCOUNT = w3.eth.accounts[0]


# =====================================
# LOAD ABI
# =====================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ABI_PATH = os.path.join(BASE_DIR, "contracts", "abi.json")

with open(ABI_PATH) as f:
    ABI = json.load(f)


# =====================================
# CONTRACT
# =====================================

CONTRACT_ADDRESS = "0xE785bEc19a13F61E3ce861F42bE5a75c8918D721"
PRIVATE_KEY = "0xe1b284ae72e84bceba8a27337d16043e621552d5f2070fe6b45a8fa2bc4c52cf"  # for ACCOUNT[0]

contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=ABI
)

print("Connected to:", contract.address)
print("Account:", ACCOUNT)
print("Balance:", w3.eth.get_balance(ACCOUNT))

# =====================================
# BLOCKCHAIN FUNCTIONS
# =====================================

def generate_key():

    tx = contract.functions.generateKey().transact({
        "from": ACCOUNT
    })

    w3.eth.wait_for_transaction_receipt(tx)



def get_my_key():

    return contract.functions.getMyKey().call({
        "from": ACCOUNT
    })



def verify_key(user, key):

    return contract.functions.verifyKey(user, key).call()



def log_access(pid):

    nonce = w3.eth.get_transaction_count(ACCOUNT)

    tx = contract.functions.logAccess(pid).build_transaction({
        "from": ACCOUNT,
        "nonce": nonce,
        "gas": 3000000,
        "gasPrice": w3.to_wei("20", "gwei")
    })

    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return tx_hash.hex()

def register_doctor(wallet):

    tx = contract.functions.registerDoctor(wallet).transact({
        "from": ACCOUNT   # admin
    })

    w3.eth.wait_for_transaction_receipt(tx)

def is_doctor(address):
    return contract.functions.isDoctor(address).call()

def register_patient(pid, wallet):

    tx = contract.functions.registerPatient(
        pid,
        wallet
    ).transact({
        "from": ACCOUNT
    })

    w3.eth.wait_for_transaction_receipt(tx)

def get_access_logs(pid):
    doctors, times, emergencies = contract.functions.getAccessLogs(pid).call()
    return doctors, times, emergencies

def get_access_logs_as_patient(pid, private_key):

    try:
        # Derive patient account
        account = w3.eth.account.from_key(private_key).address

        # Call smart contract (3 return values now)
        doctors, times, emergencies = contract.functions.getAccessLogs(
            pid
        ).call({
            "from": account
        })

        return doctors, times, emergencies

    except Exception as e:
        raise Exception(f"Access denied: {e}")

def generate_emergency():

    nonce = w3.eth.get_transaction_count(ACCOUNT)

    tx = contract.functions.generateEmergencyAccess().build_transaction({
        "from": ACCOUNT,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.to_wei("20", "gwei")
    })

    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    tx_hash = w3.eth.send_raw_transaction(
        signed.raw_transaction
    )

    return tx_hash.hex()