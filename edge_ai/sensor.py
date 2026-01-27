import random

def generate_data():
    return {
        "heart": random.randint(60, 130),
        "temp": round(random.uniform(36, 39.5), 1),
        "spo2": random.randint(88, 100)
    }
