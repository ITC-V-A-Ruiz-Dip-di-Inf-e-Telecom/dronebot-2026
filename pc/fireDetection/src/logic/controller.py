import time

class DetectionController:
    def __init__(self, confirm_frames=3) -> None:
        self.confirm_frames = confirm_frames
        self.streak = 0
        self.total_detections = 0
        self.frame_count = 0
        self.last_time = time.time()
        self.fps = 0

    def update_fps(self) -> None:
        self.frame_count += 1

        if self.frame_count >= 10:
            now = time.time()
            self.fps = self.frame_count / (now - self.last_time)
            self.frame_count = 0
            self.last_time = now

    def process(self, detections) -> bool:

        self.update_fps()

        if len(detections) > 0:
            self.streak += 1
        else:
            self.streak = 0

        if self.streak >= self.confirm_frames:
            self.total_detections += 1
            self.streak = 0
            return True

        return False
