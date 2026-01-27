def detect(data):

    if data["heart"] > 110:
        return "ALERT"

    if data["temp"] > 38:
        return "ALERT"

    if data["spo2"] < 92:
        return "ALERT"

    return "NORMAL"
