import subprocess
import cv2
import numpy as np

class ADBCapture:
    def __init__(self) -> None:
        pass

    def get_frame(self):
        process = subprocess.Popen(
                ['adb', 'exec-out', 'screencap', '-p'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )

        screenshot, _ = process.communicate()

        if process.returncode != 0:
            return None

        img_array = np.frombuffer(screenshot, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        return frame
