import time
import config

class DetectionController:
    def __init__(self) -> None:
        self.confirm_frames = config.FIRE_CONFIR_FRAMES
        self.min_fire_area = config.MIN_FIRE_AREA
        self.max_fire_shift = config.MAX_FIRE_SHIFT

        self.streak = 0
        self.total_detections = 0

        self.last_fire_box: tuple | None = None
        self.confirmed_fire_box: tuple | None = None
        self.fire_center: tuple[int, int] | None = None
        self.fire_radius_px: int | None = None

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

    def process(self, detections: list) -> bool:
        self.update_fps()

        valid_fire = None

        # Filter by area
        for detec in detections:
            x1, y1, x2, y2 = detec["box"]
            area = (x2 - x1) * (y2 - y1)

            if area >= self.min_fire_area:
                valid_fire = detec["box"]
                print(f" | Fire area: {area:.0f}", end="")
                break

        if valid_fire is None:
            self.streak = 0
            self.last_fire_box = None
            return False

        # Stability check
        if self.last_fire_box is not None:
            shift = self._box_shift(valid_fire, self.last_fire_box)

            print(f" | Shift: {shift:.1f}", end="")

            if shift >= self.max_fire_shift:
                print(f" (>{self.max_fire_shift})", end="")
                self.streak = 0
                self.last_fire_box = valid_fire
                return False

        self.last_fire_box = valid_fire
        self.streak += 1

        # Confirm after consecutive frames
        if self.streak >= self.confirm_frames:
            self.confirmed_fire_box = valid_fire
            x1, y1, x2, y2 = valid_fire
            self.fire_center = ((x1 + x2) // 2, (y1 + y2) // 2)
            self.fire_radius_px = min(x2 - x1, y2 - y1) // 2
            self.total_detections += 1
            self.streak = 0
            return True

        return False

    def _box_shift(self, box1, box2):
        x1a, y1a, x2a, y2a = box1
        x1b, y1b, x2b, y2b = box2

        centre1 = ((x1a + x2a) // 2, (y1a + y2a) // 2)
        centre2 = ((x1b + x2b) // 2, (y1b + y2b) // 2)

        return ((centre1[0] - centre2[0]) ** 2 +
                (centre1[1] - centre2[1]) ** 2) ** 0.5
