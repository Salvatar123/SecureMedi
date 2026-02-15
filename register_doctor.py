from blockchain.connector import register_doctor
from blockchain.connector import w3

# Pick any Ganache account you want as doctor
doctor_wallet = w3.eth.accounts[0]   # or [1], [2], etc.

register_doctor(doctor_wallet)

print("Doctor registered:", doctor_wallet)
