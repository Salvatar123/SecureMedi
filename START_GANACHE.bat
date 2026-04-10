@echo off
REM Start Ganache with deterministic test mnemonic for consistent wallet addresses
REM This ensures the same 10 accounts are generated every time Ganache starts

echo ========================================
echo Starting Ganache with test mnemonic
echo ========================================
echo.
echo Mnemonic: "test test test test test test test test test test test junk"
echo Accounts: 10
echo Port: 8545
echo.

REM Check if ganache-cli is installed globally
where ganache-cli >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo Running: ganache-cli --mnemonic "test test test test test test test test test test test junk" --accounts 10
    ganache-cli --mnemonic "test test test test test test test test test test test junk" --accounts 10
    goto :done
)

REM Check if ganache is available (newer version)
where ganache >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo Running: ganache --mnemonic "test test test test test test test test test test test junk" --accounts 10
    ganache --mnemonic "test test test test test test test test test test test junk" --accounts 10
    goto :done
)

REM Try to run via npm/npx
echo Running: npx ganache --mnemonic "test test test test test test test test test test test junk" --accounts 10
npx ganache --mnemonic "test test test test test test test test test test test junk" --accounts 10

:done
echo.
echo Ganache stopped.
pause
