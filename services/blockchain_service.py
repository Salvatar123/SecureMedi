"""
Blockchain service layer.
Wraps Web3 interactions and smart contract calls.
Removes hardcoded credentials and makes them configurable.
"""

import json
import logging
import os
from typing import Tuple
from web3 import Web3
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BlockchainService:
    """Service for blockchain operations."""

    def __init__(self):
        """Initialize blockchain connection."""
        self.settings = settings
        self.w3 = None
        self.contract = None
        self.account = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize Web3 connection and load contract."""
        try:
            # Connect to blockchain network
            self.w3 = Web3(Web3.HTTPProvider(self.settings.GANACHE_URL))

            if not self.w3.is_connected():
                raise ConnectionError(
                    f"Cannot connect to blockchain at {self.settings.GANACHE_URL}"
                )

            logger.info(f"Connected to blockchain: {self.settings.GANACHE_URL}")

            # Get default account
            self.account = self.w3.eth.accounts[0]
            logger.info(f"Using account: {self.account}")

            # Load ABI
            abi_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "contracts", "abi.json"
            )
            with open(abi_path) as f:
                abi = json.load(f)

            # Initialize contract
            self.contract = self.w3.eth.contract(address=self.settings.CONTRACT_ADDRESS, abi=abi)

            logger.info(f"Contract loaded: {self.settings.CONTRACT_ADDRESS}")
            balance = self.w3.eth.get_balance(self.account)
            logger.info(f"Account balance: {self.w3.from_wei(balance, 'ether')} ETH")

        except Exception as e:
            logger.error(f"Blockchain initialization failed: {e}")
            raise

    def generate_key(self) -> None:
        """Generate a new access key for the account."""
        try:
            tx = self.contract.functions.generateKey().transact({"from": self.account})
            self.w3.eth.wait_for_transaction_receipt(tx)
            logger.info("New access key generated")
        except Exception as e:
            logger.error(f"Failed to generate key: {e}")
            raise

    def get_my_key(self) -> bytes:
        """Get the access key for current account."""
        try:
            return self.contract.functions.getMyKey().call({"from": self.account})
        except Exception as e:
            logger.error(f"Failed to get key: {e}")
            raise

    def verify_key(self, user: str, key: bytes) -> bool:
        """Verify if a user has a valid access key."""
        try:
            return self.contract.functions.verifyKey(user, key).call()
        except Exception as e:
            logger.error(f"Key verification failed: {e}")
            raise

    def log_access(self, patient_id: str) -> str:
        """Log patient access on blockchain."""
        try:
            nonce = self.w3.eth.get_transaction_count(self.account)

            tx = self.contract.functions.logAccess(patient_id).build_transaction(
                {
                    "from": self.account,
                    "nonce": nonce,
                    "gas": self.settings.GAS_LIMIT,
                    "gasPrice": self.w3.to_wei(self.settings.GAS_PRICE_GWEI, "gwei"),
                }
            )

            signed = self.w3.eth.account.sign_transaction(tx, self.settings.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
            self.w3.eth.wait_for_transaction_receipt(tx_hash)

            logger.info(f"Access logged for patient {patient_id}: {tx_hash.hex()}")
            return tx_hash.hex()

        except Exception as e:
            logger.error(f"Failed to log access: {e}")
            raise

    def register_doctor(self, wallet: str) -> None:
        """Register a doctor wallet."""
        try:
            tx = self.contract.functions.registerDoctor(wallet).transact({"from": self.account})
            self.w3.eth.wait_for_transaction_receipt(tx)
            logger.info(f"Doctor registered: {wallet}")
        except Exception as e:
            logger.error(f"Failed to register doctor: {e}")
            raise

    def is_doctor(self, address: str) -> bool:
        """Check if an address is a registered doctor."""
        try:
            return self.contract.functions.isDoctor(address).call()
        except Exception as e:
            logger.error(f"Failed to check doctor status: {e}")
            raise

    def register_patient(self, patient_id: str, wallet: str) -> None:
        """Register a patient with their wallet."""
        try:
            tx = self.contract.functions.registerPatient(patient_id, wallet).transact(
                {"from": self.account}
            )
            self.w3.eth.wait_for_transaction_receipt(tx)
            logger.info(f"Patient registered: {patient_id}")
        except Exception as e:
            logger.error(f"Failed to register patient: {e}")
            raise

    def get_access_logs(self, patient_id: str) -> Tuple[list, list, list]:
        """Get access logs for a patient."""
        try:
            doctors, times, emergencies = self.contract.functions.getAccessLogs(patient_id).call()
            logger.info(f"Retrieved {len(doctors)} access logs for patient {patient_id}")
            return doctors, times, emergencies
        except Exception as e:
            logger.error(f"Failed to get access logs: {e}")
            raise

    def get_access_logs_as_patient(
        self, patient_id: str, private_key: str
    ) -> Tuple[list, list, list]:
        """Get access logs as a patient using their private key."""
        try:
            account = self.w3.eth.account.from_key(private_key).address
            doctors, times, emergencies = self.contract.functions.getAccessLogs(patient_id).call(
                {"from": account}
            )
            logger.info(f"Patient {patient_id} retrieved their access logs")
            return doctors, times, emergencies
        except Exception as e:
            logger.error(f"Failed to get patient access logs: {e}")
            raise

    def generate_emergency_access(self) -> str:
        """Generate an emergency access token."""
        try:
            nonce = self.w3.eth.get_transaction_count(self.account)

            tx = self.contract.functions.generateEmergencyAccess().build_transaction(
                {
                    "from": self.account,
                    "nonce": nonce,
                    "gas": 200000,
                    "gasPrice": self.w3.to_wei(self.settings.GAS_PRICE_GWEI, "gwei"),
                }
            )

            signed = self.w3.eth.account.sign_transaction(tx, self.settings.PRIVATE_KEY)
            tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)

            logger.info(f"Emergency access generated: {tx_hash.hex()}")
            return tx_hash.hex()

        except Exception as e:
            logger.error(f"Failed to generate emergency access: {e}")
            raise
