import requests
import config

class FlaskClient:

    def __init__(self) -> None:
        self.base_url = config.RASPBERRY_PI_URL.rstrip("/")
        self.timeout = 3

    def send_phase1_complete(self) -> bool:
        return self._post("/start_hunt")

    def send_rover_in_fire(self) -> bool:
        return self._post("/stop_all")

    def _post(self, endpoint: str) -> bool:
        try:
            resp = requests.post(f"{self.base_url}{endpoint}", timeout=self.timeout)
            print(f"[HTTP] POST {endpoint} → {resp.status_code}")
            return resp.status_code == 200
        except Exception as e:
            print(f"[HTTP] Failed POST {endpoint}: {e}")
            return False
