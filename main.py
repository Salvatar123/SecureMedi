from edge_ai.sensor import generate_data
from edge_ai.detector import detect
from logs.logger import save
import time

while True:

    data = generate_data()
    status = detect(data)

    print("Vitals:", data)
    print("Status:", status)
    print("------------------")

    save(data, status)

    time.sleep(3)
