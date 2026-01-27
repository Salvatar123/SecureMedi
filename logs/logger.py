import csv
import os

FILE = "logs/data.csv"

def save(data, status):

    file_exists = os.path.isfile(FILE)

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["heart", "temp", "spo2", "status"])

        writer.writerow([
            data["heart"],
            data["temp"],
            data["spo2"],
            status
        ])
