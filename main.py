import time

# Edge AI
from edge_ai.sensor import generate_data
from edge_ai.detector import detect

# Local logger
from logs.logger import save

# Blockchain
from blockchain.connector import send_record


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
                    tx = send_record(
                        "P001",
                        str(data),
                        status
                    )

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
