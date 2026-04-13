import cv2
import config

from detection.yolo_detector import YOLODetector
from detection.aruco_detector import ARUCODetector
from ui.render import Render
from logic.controller import DetectionController
from utils.evidence_saver import EvidenceSaver
from utils.utils import full_inside, iou

cap = cv2.VideoCapture(config.VIDEO_SOURCE)

detector = YOLODetector()
aruco = ARUCODetector()
renderer = Render()
controller = DetectionController()
saver = EvidenceSaver()

PHASE = 1
rover_streak = 0

cv2.namedWindow("Fire Detector", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Fire Detector", 900, 600)

while True:

    ret, frame =cap.read()
    if not ret or frame is None:
        continue

    if PHASE == 1:
        detections = detector.detect(frame)

        # Debug detection count
        print(f"[Phase 1] Detections: {len(detections)}", end="")

        alert = controller.process(detections)

        # Debug streak progress
        print(f" | Streak: {controller.streak}/{controller.confirm_frames}", end="")

        if alert:
            print(" | Yes FIRE CONFIRMED!")
        else:
            print()

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
            print("\n" + "="*60)
            print("TRANSITIONING TO PHASE 2")
            print("="*60 + "\n")
            PHASE = 2

            if config.SAVE_EVIDENCE:
                path = saver.save(frame)
                print(f"Fire Saved -> {path}")

    elif PHASE == 2:

        fire_detection = detector.detect(frame)

        fire_box = None

        for detec in fire_detection:
            x1, y1, x2, y2 = detec["box"]
            area = (x2 - x1) * (y2 - y1)

            if area >= config.MIN_FIRE_AREA:
                fire_box = detec["box"]
                break

        # Draw fire box first
        frame = renderer.draw(frame, fire_detection)

        rover_box = aruco.detect(frame)

        # Debug rover detection status
        print(f"[Phase 2] Fire Box: {'Yes' if fire_box else 'No'} | Rover Detected: {'Yes' if rover_box else 'No'}", end="")

        if fire_box and rover_box:
            inside = full_inside(rover_box, fire_box)
            overlap = iou(rover_box, fire_box)

            # Debug containment metrics
            print(f" | Inside: {inside} | IoU: {overlap:.3f}", end="")

            if inside or overlap > config.MIN_OVERLAP_AREA:
                rover_streak += 1
                print(f" | Streak: {rover_streak}/{config.ROVER_CONFIRM_FRAMES} ✓ CONTAINED", end="")
                # Draw rover box
                frame = renderer.draw_rover(frame, rover_box, status="contained")
            else:
                rover_streak = 0
                print(f" | Streak: {rover_streak}/{config.ROVER_CONFIRM_FRAMES} ✗ NOT CONTAINED", end="")
                # Draw rover box
                frame = renderer.draw_rover(frame, rover_box, status="not_contained")

            if rover_streak >= config.ROVER_CONFIRM_FRAMES:
                print("\n\n" + "="*60)
                print("ROVER CONTAINMENT CONFIRMED")
                print("="*60 + "\n")

                if config.SAVE_EVIDENCE:
                    path = saver.save(frame)
                    print(f"Final Evidence Saved -> {path}")
                break
        elif rover_box:
            # Rover detected but no fire box
            print(f" | Status: Waiting for fire box", end="")
            frame = renderer.draw_rover(frame, rover_box, status="detected")
        else:
            # Reset streak if no rover detected
            if rover_streak > 0:
                print(f" | Streak RESET (was {rover_streak})", end="")
                rover_streak = 0


    # Display the frame
    cv2.imshow("Fire Detector", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
