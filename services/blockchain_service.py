"""
Blockchain service layer.
Wraps Web3 interactions and smart contract calls.
Removes hardcoded credentials and makes them configurable.
"""

import json
import logging
import os
from typing import Tuple
from config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Lazy import Web3 to avoid pkg_resources issues
Web3 = None


def _ensure_web3():
    """Lazy load Web3 on first use."""
    global Web3
    if Web3 is None:
        try:
            from web3 import Web3 as _Web3
            Web3 = _Web3
        except (ImportError, ModuleNotFoundError) as e:
            logger.error(f"Failed to import Web3: {e}")
            logger.warning("Web3/Blockchain functionality will not be available")


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
            # Lazy load Web3
            _ensure_web3()
            
            if Web3 is None:
                logger.warning("Web3 not available. Blockchain features will be disabled.")
                return
            
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
            logger.warning("The application will continue without blockchain functionality")

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

    def emergency_access(self, patient_id: str, key: str) -> dict:
        """
        Emergency access to patient data.
        This function will bypass normal authentication and use a one-time key
        to access a patient's data.
        """
        try:
            # For now, we'll just check if the key is valid.
            # In a real implementation, we would also check if the key is a valid one-time key
            # and if the patient_id is valid.
            is_valid_key = len(key) > 0  # Dummy validation

            if not is_valid_key:
                raise ValueError("Invalid emergency access key")

            # Dummy data, replace with actual data retrieval from blockchain/database
            patient_data = {
                "patient_id": patient_id,
                "name": "John Doe",
                "vitals": {
                    "heart_rate": 80,
                    "temperature": 98.6,
                    "blood_pressure": "120/80"
                }
            }
            return patient_data
        except Exception as e:
            logger.error(f"Emergency access failed: {e}")
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
            # Use transact() for auto-signing on Ganache
            tx = self.contract.functions.logAccess(patient_id).transact({"from": self.account})
            self.w3.eth.wait_for_transaction_receipt(tx)

            logger.info(f"Access logged for patient {patient_id}: {tx.hex()}")
            return tx.hex()

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

    def is_patient(self, patient_id: str) -> bool:
        """Check if a patient ID is registered on chain."""
        try:
            return self.contract.functions.isPatientRegistered(patient_id).call()
        except Exception as e:
            logger.error(f"Failed to check patient status: {e}")
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
