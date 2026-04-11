"""Wallet Service - Manages wallet generation and assignment"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from config.settings import get_settings
from eth_account import Account

logger = logging.getLogger(__name__)


class WalletService:
    """Service for wallet generation and management"""

    # Keep in sync with START_GANACHE.bat and docs.
    DEFAULT_GANACHE_MNEMONIC = "test test test test test test test test test test test junk"

    def __init__(self):
        """Initialize wallet service"""
        self.settings = get_settings()
        self.ganache_accounts = self._fetch_ganache_accounts()
        self.assigned_wallets = self._load_assigned_wallets()
        self.next_account_index = self._calculate_next_account_index()

    def _calculate_next_account_index(self) -> int:
        """Return the next unused Ganache account index based on stored assignments."""
        max_index = -1
        for record in self.assigned_wallets.values():
            idx = record.get("account_index")
            if isinstance(idx, int):
                max_index = max(max_index, idx)
        return max_index + 1

    def _used_account_indices(self) -> set[int]:
        """Return the set of assigned account indices."""
        used: set[int] = set()
        for record in self.assigned_wallets.values():
            idx = record.get("account_index")
            if isinstance(idx, int):
                used.add(idx)
        return used

    def _next_free_account_index(self) -> Optional[int]:
        """Return the first free account index from current Ganache accounts."""
        if not self.ganache_accounts:
            return None
        used = self._used_account_indices()
        for idx in range(len(self.ganache_accounts)):
            if idx not in used:
                return idx
        return None

    def _fetch_ganache_accounts(self) -> List[Dict]:
        """Fetch accounts from running Ganache instance"""
        try:
            from web3 import Web3

            w3 = Web3(Web3.HTTPProvider(self.settings.GANACHE_URL))
            if not w3.is_connected():
                logger.warning(f"Could not connect to Ganache at {self.settings.GANACHE_URL}")
                return []

            accounts = w3.eth.accounts
            if not accounts:
                logger.warning("No accounts found in Ganache")
                return []

            ganache_accounts = [{"address": account} for account in accounts]
            logger.info(f"Fetched {len(ganache_accounts)} accounts from Ganache")
            return ganache_accounts
        except Exception as e:
            logger.error(f"Failed to fetch Ganache accounts: {e}")
            logger.warning("Will fall back to offline mode or empty account list")
            return []

    def _derive_private_key_from_mnemonic(self, mnemonic: str, account_index: int) -> Optional[str]:
        """Derive private key from mnemonic using BIP44 m/44'/60'/0'/0/{index}."""
        try:
            Account.enable_unaudited_hdwallet_features()
            account = Account.from_mnemonic(
                mnemonic,
                account_path=f"m/44'/60'/0'/0/{account_index}",
            )

            if account_index < len(self.ganache_accounts):
                expected_address = (self.ganache_accounts[account_index].get("address") or "").lower()
                if expected_address and account.address.lower() != expected_address:
                    logger.warning(
                        "Derived key/address mismatch at index %s: derived=%s expected=%s",
                        account_index,
                        account.address,
                        expected_address,
                    )
                    return None

            return account.key.hex().replace("0x", "")
        except Exception as e:
            logger.error(f"Failed to derive private key: {e}")
            return None

    def _repair_assigned_wallet_keys(self) -> bool:
        """Repair stored private keys if they do not match their recorded address."""
        repaired = False

        for user_id, record in self.assigned_wallets.items():
            address = (record.get("address") or "").lower()
            private_key = (record.get("private_key") or "").replace("0x", "")
            account_index = record.get("account_index")

            if not address or account_index is None:
                continue

            is_valid_pair = False
            if private_key:
                try:
                    derived = Account.from_key(bytes.fromhex(private_key)).address.lower()
                    is_valid_pair = derived == address
                except Exception:
                    is_valid_pair = False

            if is_valid_pair:
                continue

            corrected_key = self._derive_private_key_from_mnemonic(
                self.DEFAULT_GANACHE_MNEMONIC,
                int(account_index),
            )
            if not corrected_key:
                logger.warning(f"Could not repair private key for {user_id} at index {account_index}")
                continue

            corrected_address = Account.from_key(bytes.fromhex(corrected_key)).address.lower()
            if corrected_address != address:
                logger.warning(
                    "Repair skipped for %s: corrected address %s does not match %s",
                    user_id,
                    corrected_address,
                    address,
                )
                continue

            record["private_key"] = corrected_key
            repaired = True
            logger.info(f"Repaired wallet private key for {user_id}")

        return repaired

    def _load_assigned_wallets(self) -> Dict[str, Dict]:
        """Load previously assigned wallets from file and auto-repair invalid keys."""
        wallets_file = "wallets_assigned.json"
        if os.path.exists(wallets_file):
            try:
                with open(wallets_file, "r") as f:
                    wallets = json.load(f)

                self.assigned_wallets = wallets
                if self._repair_assigned_wallet_keys():
                    self._save_assigned_wallets()

                return self.assigned_wallets
            except Exception as e:
                logger.warning(f"Could not load assigned wallets: {e}")
        return {}

    def _save_assigned_wallets(self) -> None:
        """Save assigned wallets to file"""
        try:
            with open("wallets_assigned.json", "w") as f:
                json.dump(self.assigned_wallets, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save assigned wallets: {e}")

    def generate_wallet(self, user_id: str, user_type: str = "doctor") -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Generate and assign a deterministic Ganache wallet for a user."""
        if user_id in self.assigned_wallets:
            logger.warning(f"User {user_id} already has a wallet assigned")
            account = self.assigned_wallets[user_id]
            return account.get("address"), None, "User already has a wallet assigned"

        self.ganache_accounts = self._fetch_ganache_accounts()
        if not self.ganache_accounts:
            error = "No Ganache accounts available. Is Ganache running?"
            logger.error(error)
            return None, None, error

        next_account_index = self._next_free_account_index()
        if next_account_index is None:
            error = f"No more Ganache accounts available. Max {len(self.ganache_accounts)} users."
            logger.error(error)
            return None, None, error

        account = self.ganache_accounts[next_account_index]
        wallet_address = account["address"]

        private_key = self._derive_private_key_from_mnemonic(
            self.DEFAULT_GANACHE_MNEMONIC,
            next_account_index,
        )
        if not private_key:
            error = f"Could not derive private key for account {next_account_index}"
            logger.error(error)
            return None, None, error

        self.assigned_wallets[user_id] = {
            "address": wallet_address,
            "private_key": private_key,
            "user_type": user_type,
            "account_index": next_account_index,
            "assigned_at": datetime.utcnow().isoformat(),
        }
        self.next_account_index = self._calculate_next_account_index()
        self._save_assigned_wallets()

        logger.info(f"Generated wallet for {user_type} {user_id}: {wallet_address}")
        return wallet_address, private_key, None

    def unassign_wallet(
        self,
        user_id: Optional[str] = None,
        address: Optional[str] = None,
        user_type: Optional[str] = None,
    ) -> bool:
        """Remove an assigned wallet mapping by user ID or wallet address."""
        target_key: Optional[str] = None

        if user_id and user_id in self.assigned_wallets:
            record = self.assigned_wallets[user_id]
            if user_type is None or record.get("user_type") == user_type:
                target_key = user_id

        if target_key is None and address:
            normalized = address.lower()
            for key, record in self.assigned_wallets.items():
                if (record.get("address") or "").lower() != normalized:
                    continue
                if user_type and record.get("user_type") != user_type:
                    continue
                target_key = key
                break

        if target_key is None:
            return False

        removed = self.assigned_wallets.pop(target_key, None)
        if removed is None:
            return False

        self.next_account_index = self._calculate_next_account_index()
        self._save_assigned_wallets()
        logger.info(f"Unassigned wallet for {target_key}")
        return True

    def get_wallet(self, user_id: str) -> Optional[Dict]:
        """Get assigned wallet for a user"""
        return self.assigned_wallets.get(user_id)

    def list_assigned_wallets(self) -> Dict:
        """List all assigned wallets"""
        return self.assigned_wallets

    def get_available_count(self) -> int:
        """Get number of available accounts"""
        return max(0, len(self.ganache_accounts) - len(self._used_account_indices()))

    def get_total_count(self) -> int:
        """Get total number of Ganache accounts"""
        return len(self.ganache_accounts)


_wallet_service = None


def get_wallet_service() -> WalletService:
    """Get or create wallet service instance"""
    global _wallet_service
    if _wallet_service is None:
        _wallet_service = WalletService()
    return _wallet_service
