import time

# Edge AI
from dashboard import patient
from edge_ai.sensor import generate_data
from edge_ai.detector import detect

# Local logger
from logger import save

# Blockchain
from blockchain.connector import log_access


def main():

    print("🚀 secureMedi System Started...")
    print("Press Ctrl + C to stop safely.\n")

    try:
        while True:

            # 1. Generate sensor data
            data = generate_data()

            # 2. Detect anomaly
            status = detect(data)

            # 3. Print output
            print("Vitals:", data)
            print("Status:", status)

            # 4. Save locally
            save(data, status)

            # 5. Send ALERT to blockchain
            if status == "ALERT":

                try:
                    patient_id = "P001"
                    tx = log_access(patient_id)

                    print("✅ Stored on Blockchain")
                    print("TX Hash:", tx)

                except Exception as e:
                    print("❌ Blockchain Error:", e)

            print("-" * 40)

            time.sleep(3)

    except KeyboardInterrupt:
        print("\n🛑 secureMedi stopped safely.")


if __name__ == "__main__":
    main()
