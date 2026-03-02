from capture.adb_capture import ADBCapture
from detection.yolo_detector import Detector
from ui.render import Render
from logic.controller import DetectionController
from utils.evidence_saver import EvidenceSaver
import cv2


def resize_for_display(frame, max_width=900):
    h, w = frame.shape[:2]

    if w <= max_width:
        return frame

    scale = max_width / w
    return cv2.resize(frame, None, fx=scale, fy=scale)


cap = cv2.VideoCapture("/dev/video10")
detector = Detector()
renderer = Render()
controller = DetectionController(confirm_frames=3)
saver = EvidenceSaver()

cv2.namedWindow("Fire Detector", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Fire Detector", 900, 600)

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    detections = detector.detect(frame)
    alert = controller.process(detections)
    
    # Draw detections first
    frame = renderer.draw(frame, detections)
    
    # Draw info panel with status
    frame = renderer.draw_info(
        frame,
        controller.fps,
        controller.total_detections,
        detector.device,
        fire_alert=alert
    )

    if alert:
        print("FIRE CONFIRMED")
        path = saver.save(frame)
        print(f"Fire captured and saved -> {path}")

    display = resize_for_display(frame)
    cv2.imshow("Fire Detector", display)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
