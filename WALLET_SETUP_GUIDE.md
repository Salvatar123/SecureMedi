# Dynamic Wallet Generation - Setup Guide

## Overview

The wallet service now **dynamically fetches accounts from Ganache** at runtime instead of using hardcoded addresses. This means:

✅ **Wallets persist** across Ganache restarts (if using fixed mnemonic)
✅ **Automatic account discovery** from running Ganache instance  
✅ **Private key derivation** from standard BIP44 path
✅ **Graceful fallback** if Ganache isn't available

## Starting Ganache Correctly

### Option 1: Use the Provided Script (Easiest)

**Windows:**
```bash
START_GANACHE.bat
```

This automatically starts Ganache with the correct mnemonic.

### Option 2: Manual CLI

**Install Ganache (if not already installed):**
```bash
npm install -g ganache-cli
# or for newer versions:
npm install -g ganache
```

**Start with deterministic mnemonic:**
```bash
ganache-cli --mnemonic "test test test test test test test test test test test junk" --accounts 10
```

Or for newer versions:
```bash
ganache --mnemonic "test test test test test test test test test test test junk" --accounts 10
```

### Option 3: Ganache GUI

1. Download [Ganache GUI](https://www.trufflesuite.com/ganache)
2. Click "New Workspace"
3. Go to **Accounts & Keys** tab
4. Set **Mnemonic**: `test test test test test test test test test test test junk`
5. Set **Number of Accounts**: 10
6. Start the workspace

## How It Works

### Account Setup

When Ganache starts with the mnemonic `"test test test test test test test test test test test junk"`, it generates 10 accounts:

```
Account 0: 0x627306090abaB3A6e1400e9345bC60c78a8BEf57
Account 1: 0xf17f52151EbEF6C7334FAD080C5704DAAB7C2E35
Account 2: 0xC5fdf4076b8F3A5357c5E395ab970B5B54098Fef
... (10 total)
```

### Creating a Doctor/Patient

1. **Admin adds doctor in dashboard** → Name: "Dr. Smith", Email: "dr@example.com"
2. **System fetches from Ganache** → Gets list of available accounts
3. **Auto-assigns wallet** → Account #0 (0x627306...)
4. **Derives private key** → Uses BIP44 standard path derivation
5. **Saves to Supabase** → Stores doctor info + wallet address
6. **Registers on blockchain** → Smart contract updated
7. **Shows credentials** → Admin sees wallet address + private key to give to doctor

### Doctor Logs In

1. **Doctor enters** → Address: `0x627306...`, Private Key: `c87509a...`
2. **Auth service checks blockchain** → `is_doctor(0x627306...)` ✅
3. **Login succeeds** → JWT token issued
4. **Dashboard loads** → Shows doctor's health records

## Wallet Status

Check available wallets in admin dashboard:

```
Wallet Status: 9 of 10 accounts available
```

This refreshes dynamically based on what's running in Ganache.

## Troubleshooting

### "No Ganache accounts available. Is Ganache running?"

**Solution:** Make sure Ganache is running on `http://localhost:8545`

```bash
# Check if Ganache is running
curl http://localhost:8545
```

### Private keys not generating

**Solution:** Wallet service falls back to hardcoded keys if derivation fails. Check logs:

```
[WARNING] Could not derive private key, using standard Ganache keys
```

This is **normal** if hdwallet package isn't installed.

### Getting different accounts each time

**Problem:** Ganache started **without** a fixed mnemonic
**Solution:** Always start with: 
```bash
ganache --mnemonic "test test test test test test test test test test test junk"
```

## Standard Account Private Keys

If private key derivation fails, these are the hardcoded fallback keys for the test mnemonic:

```python
{
    0: "4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d",
    1: "6cbed15c793ce57650b9877cf6fa156fad16cfe22666dc3a79c1e1ea88e44e61",
    2: "6370fd033278c143179d81c5526140625662b8dab6c7f509cc0d3fd4fe4426a1",
    3: "646f1ce2fdad0e6deeeb5c7e8e5543bdde19e7ee9f40f15c42febc8d456e6fa1",
    4: "add53f9b7f244f5b90e3f881e59f2b48cd4d77e0d0f4f4e6c7d72e6d1e6d1e6d",
    5: "395df67f0c2d2d187c43529f0980be6d6de1d849618e8a1cabc87467b5cc6511",
    6: "e485d098507f54e7733a205420dfddbe58db035fa577fc294ebd4db35b57de33",
    7: "a453611d9419d0991e7db8b8a88ed1d27c3a51122a895a245334d0560e4d9194",
    8: "829e924fdf94acb08713b2bac6499383128fd341daf101ec8f9f1619f4fadb58",
    9: "f1cc7154e17529891a18d158646e3434dac11801d7a53f69d60427a4ca4cecb7",
}
```

## Development vs Production

### Development
- Use Ganache with test mnemonic (✅ current setup)
- 10 test accounts pre-configured
- Instant account creation

### Production
- Use **real blockchain** (Ethereum mainnet or testnet)
- Generate accounts with **MetaMask** or **hardware wallet**
- Update GANACHE_URL in config to point to real blockchain
- Wallet service will work with any EVM-compatible chain

## Reset Wallets

To clear wallet assignments and start fresh:

```bash
# Delete the wallet tracking file
rm wallets_assigned.json  # Linux/Mac
del wallets_assigned.json  # Windows
```

The next admin addition will start assigning from Account #0 again.

## Files

- `START_GANACHE.bat` - Windows batch script to start Ganache correctly
- `backend/app/services/wallet_service.py` - Dynamic wallet generation service
- `wallets_assigned.json` - Tracks which user got which wallet (auto-created)
