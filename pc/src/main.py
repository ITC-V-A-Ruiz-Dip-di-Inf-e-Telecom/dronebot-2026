import cv2
import config

from detection.yolo_detector import YOLODetector
from detection.aruco_detector import ARUCODetector
from ui.render import Render
from logic.controller import DetectionController
from utils.evidence_saver import EvidenceSaver
from utils.utils import rover_inside_fire_circle

cap = cv2.VideoCapture(config.VIDEO_SOURCE)

detector = YOLODetector()
aruco = ARUCODetector()
renderer = Render()
controller = DetectionController()
saver = EvidenceSaver()

PHASE = 1

# Phase 2 state
fire_locked = False
fire_lock_streak = 0
fire_lock_last = None # last fire box used for shift comparison
rover_streak = 0

cv2.namedWindow("Fire Detector", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Fire Detector", 900, 600)

while True:

    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    if PHASE == 1:
        detections = detector.detect(frame)

        print(f"[Phase 1] Detections: {len(detections)}", end="")

        alert = controller.process(detections)

        print(f" | Streak: {controller.streak}/{controller.confirm_frames}", end="")

        if alert:
            print(" | FIRE CONFIRMED!")
        else:
            print()

        frame = renderer.draw(frame, detections)
        frame = renderer.draw_info(
            frame,
            controller.fps,
            controller.total_detections,
            detector.device,
            fire_alert=alert
        )

        if alert:
            if config.SAVE_EVIDENCE:
                path = saver.save(frame)
                print(f"Fire evidence saved → {path}")

            print("\n" + "="*60)
            print("PHASE 1 COMPLETE — TRANSITIONING TO PHASE 2")
            print("  Fly to the rover area.")
            print("="*60 + "\n")
            PHASE = 2

    elif PHASE == 2:

        controller.update_fps()

        fire_detection = detector.detect(frame)
        frame = renderer.draw(frame, fire_detection)

        # 2a hover until the circle is stable and locked 
        if not fire_locked:

            best_fire = None
            for detec in fire_detection:
                x1, y1, x2, y2 = detec["box"]
                if (x2 - x1) * (y2 - y1) >= config.MIN_FIRE_AREA:
                    best_fire = detec["box"]
                    break

            if best_fire is not None:
                if fire_lock_last is not None:
                    ax1, ay1, ax2, ay2 = best_fire
                    bx1, by1, bx2, by2 = fire_lock_last
                    shift = (((ax1 + ax2) / 2 - (bx1 + bx2) / 2) ** 2 +
                             ((ay1 + ay2) / 2 - (by1 + by2) / 2) ** 2) ** 0.5
                    fire_lock_streak = fire_lock_streak + 1 if shift < config.MAX_FIRE_SHIFT else 1
                else:
                    fire_lock_streak = 1
                fire_lock_last = best_fire
            else:
                fire_lock_streak = 0
                fire_lock_last = None

            frame = renderer.draw_phase2_info(
                frame, "locking", fire_lock_streak, config.FIRE_LOCK_FRAMES, controller.fps
            )
            print(f"[Phase 2a] Locking fire: {fire_lock_streak}/{config.FIRE_LOCK_FRAMES}", end="\r")

            if fire_lock_streak >= config.FIRE_LOCK_FRAMES and fire_lock_last is not None:
                x1, y1, x2, y2 = fire_lock_last
                controller.fire_center    = ((x1 + x2) // 2, (y1 + y2) // 2)
                controller.fire_radius_px = min(x2 - x1, y2 - y1) // 2
                fire_locked = True
                print(f"\n[Phase 2a] Circle locked — center {controller.fire_center},"
                      f" radius {controller.fire_radius_px} px")

        # 2b checks rover is inside the locked circle
        else:
            if controller.fire_center is not None:
                for detec in fire_detection:
                    x1, y1, x2, y2 = detec["box"]
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    old_cx, old_cy = controller.fire_center
                    if ((cx - old_cx) ** 2 + (cy - old_cy) ** 2) ** 0.5 <= config.MAX_FIRE_SHIFT:
                        controller.fire_center = (cx, cy)
                        break   # radius stays locked from 2a

            frame = renderer.draw_fire_circle(
                frame, controller.fire_center, controller.fire_radius_px
            )
            frame = renderer.draw_phase2_info(
                frame, "checking", rover_streak, config.ROVER_CONFIRM_FRAMES, controller.fps
            )

            rover_box = aruco.detect(frame)

            print(f"[Phase 2b] Rover: {'Yes' if rover_box else 'No '}", end="")

            if rover_box:
                contained = rover_inside_fire_circle(
                    rover_box,
                    controller.fire_center,
                    controller.fire_radius_px,
                    tolerance=config.MAX_ROVER_SHIFT
                )

                if contained:
                    rover_streak += 1
                    print(f" | Streak: {rover_streak}/{config.ROVER_CONFIRM_FRAMES} v", end="")
                    frame = renderer.draw_rover(frame, rover_box, status="contained")
                else:
                    rover_streak = 0
                    print(f" | Streak: 0/{config.ROVER_CONFIRM_FRAMES} x", end="")
                    frame = renderer.draw_rover(frame, rover_box, status="not_contained")

                if rover_streak >= config.ROVER_CONFIRM_FRAMES:
                    print()
                    print("\n" + "="*60)
                    print("ROVER CONTAINMENT CONFIRMED — RACE COMPLETE")
                    print("="*60 + "\n")

                    if config.SAVE_EVIDENCE:
                        path = saver.save(frame)
                        print(f"Final evidence saved -> {path}")

                    break
            else:
                if rover_streak > 0:
                    print(f" | Streak RESET (was {rover_streak})", end="")
                    rover_streak = 0

            print()

    cv2.imshow("Fire Detector", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
