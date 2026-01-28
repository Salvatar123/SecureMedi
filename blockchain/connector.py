from web3 import Web3
import json

# Connect to Ganache
GANACHE_URL = "http://127.0.0.1:7545"

w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

if not w3.is_connected():
    raise Exception("❌ Ganache not connected")

# Paste from Ganache
PRIVATE_KEY = "0xeed6a7d1eeb36fb173859524ff3324c38baf9f1ab24fc434099a4f6dc7cb3f40"

ACCOUNT = w3.eth.account.from_key(PRIVATE_KEY).address

# Load ABI
with open("contracts/abi.json") as f:
    abi = json.load(f)

# Paste from Remix
CONTRACT_ADDRESS = "0x06d22FdDbc07D36e3373617C4e300bDa7F13bE5D"

contract = w3.eth.contract(
    address=CONTRACT_ADDRESS,
    abi=abi
)

def send_record(patient, vitals, status):

    nonce = w3.eth.get_transaction_count(ACCOUNT)

    tx = contract.functions.addRecord(
        patient,
        vitals,
        status
    ).build_transaction({
        "from": ACCOUNT,
        "nonce": nonce,
        "gas": 3000000,
        "gasPrice": w3.to_wei("20", "gwei")
    })

    signed = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)

    return tx_hash.hex()

def get_count():
    return contract.functions.getCount().call()
