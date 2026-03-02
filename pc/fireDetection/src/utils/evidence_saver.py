from pathlib import Path
import time
import cv2

class EvidenceSaver:
    def __init__(self, folder="evidence") -> None:
        self.folder = Path(folder)
        self.folder.mkdir(exist_ok=True)

    def save(self, image):
        timestamp = int(time.time())
        filename = self.folder / f"evidence_{timestamp}.jpg"

        cv2.imwrite(str(filename), image)

        return filename
        
