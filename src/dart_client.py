import os
import time
import requests

BASE = "https://opendart.fss.or.kr/api"

class DartClient:
    def __init__(self):
        self.key = os.getenv("DART_API_KEY")
        if not self.key:
            raise RuntimeError("DART_API_KEY is not set")
    def get(self, endpoint, params):
        params = dict(params)
        params["crtfc_key"] = self.key
        r = requests.get(BASE + "/" + endpoint + ".json", params=params, timeout=60)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "000":
            raise RuntimeError(str(data.get("status")) + ": " + str(data.get("message")))
        time.sleep(0.15)
        return data
