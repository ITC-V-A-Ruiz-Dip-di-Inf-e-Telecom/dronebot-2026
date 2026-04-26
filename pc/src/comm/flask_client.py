import logging
import time
import requests
import config

log = logging.getLogger(__name__)


class FlaskClient:

    def __init__(self) -> None:
        self.base_url = config.RASPBERRY_PI_URL.rstrip("/")
        self.timeout = 3
        self._retries = 3

    def send_phase1_complete(self) -> bool:
        return self._post("/start")

    def send_rover_in_fire(self) -> bool:
        return self._post("/stop")

    def _post(self, endpoint: str) -> bool:
        for attempt in range(1, self._retries + 1):
            try:
                resp = requests.post(f"{self.base_url}{endpoint}", timeout=self.timeout)
                log.info("POST %s → %d", endpoint, resp.status_code)
                return resp.status_code == 200
            except Exception as e:
                log.warning("POST %s attempt %d/%d failed: %s", endpoint, attempt, self._retries, e)
                if attempt < self._retries:
                    time.sleep(0.5)
        log.error("POST %s gave up after %d attempts", endpoint, self._retries)
        return False
