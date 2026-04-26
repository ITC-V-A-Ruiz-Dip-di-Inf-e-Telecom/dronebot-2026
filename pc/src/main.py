import logging
import cv2
import config
from utils.log_setup import setup as setup_logging

setup_logging()
log = logging.getLogger("main")

from detection.yolo_detector import YOLODetector
from detection.aruco_detector import ARUCODetector
from ui.render import Render
from logic.controller import DetectionController
from utils.evidence_saver import EvidenceSaver
from utils.utils import rover_inside_fire_circle
from comm.flask_client import FlaskClient

cap = cv2.VideoCapture(config.VIDEO_SOURCE)

detector = YOLODetector()
aruco = ARUCODetector()
renderer = Render()
controller = DetectionController()
saver = EvidenceSaver()
flask_client = FlaskClient()

PHASE = 1

# Phase 2 state
fire_locked = False
fire_lock_streak = 0
fire_lock_last = None
rover_streak = 0

cv2.namedWindow("Fire Detector", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Fire Detector", 900, 600)

while True:

    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    if PHASE == 1:
        detections = detector.detect(frame)

        log.debug("[Phase 1] detections=%d streak=%d/%d",
                  len(detections), controller.streak, controller.confirm_frames)

        alert = controller.process(detections)

        if alert:
            log.info("[Phase 1] FIRE CONFIRMED (total=%d)", controller.total_detections)

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
                log.info("evidence saved → %s", path)

            if not flask_client.send_phase1_complete():
                log.error("rover not notified of phase 1 — it may not start moving")

            log.info("PHASE 1 COMPLETE — transitioning to phase 2")
            PHASE = 2

    elif PHASE == 2:

        controller.update_fps()

        fire_detection = detector.detect(frame)
        frame = renderer.draw(frame, fire_detection)

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
            log.debug("[Phase 2a] lock streak=%d/%d", fire_lock_streak, config.FIRE_LOCK_FRAMES)

            if fire_lock_streak >= config.FIRE_LOCK_FRAMES and fire_lock_last is not None:
                x1, y1, x2, y2 = fire_lock_last
                controller.fire_center    = ((x1 + x2) // 2, (y1 + y2) // 2)
                controller.fire_radius_px = min(x2 - x1, y2 - y1) // 2
                fire_locked = True
                log.info("[Phase 2a] circle locked — center=%s radius=%dpx",
                         controller.fire_center, controller.fire_radius_px)

        else:
            if controller.fire_center is not None:
                for detec in fire_detection:
                    x1, y1, x2, y2 = detec["box"]
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    old_cx, old_cy = controller.fire_center
                    if ((cx - old_cx) ** 2 + (cy - old_cy) ** 2) ** 0.5 <= config.MAX_FIRE_SHIFT:
                        controller.fire_center = (cx, cy)
                        break

            frame = renderer.draw_fire_circle(
                frame, controller.fire_center, controller.fire_radius_px
            )
            frame = renderer.draw_phase2_info(
                frame, "checking", rover_streak, config.ROVER_CONFIRM_FRAMES, controller.fps
            )

            rover_box = aruco.detect(frame)

            if rover_box:
                contained = rover_inside_fire_circle(
                    rover_box,
                    controller.fire_center,
                    controller.fire_radius_px,
                    tolerance=config.MAX_ROVER_SHIFT
                )

                if contained:
                    rover_streak += 1
                    log.debug("[Phase 2b] rover streak=%d/%d contained",
                              rover_streak, config.ROVER_CONFIRM_FRAMES)
                    frame = renderer.draw_rover(frame, rover_box, status="contained")
                else:
                    if rover_streak > 0:
                        log.debug("[Phase 2b] rover streak reset (was %d)", rover_streak)
                    rover_streak = 0
                    frame = renderer.draw_rover(frame, rover_box, status="not_contained")

                if rover_streak >= config.ROVER_CONFIRM_FRAMES:
                    log.info("ROVER CONTAINMENT CONFIRMED — race complete")

                    if not flask_client.send_rover_in_fire():
                        log.error("rover not notified of containment — it may not stop")

                    if config.SAVE_EVIDENCE:
                        path = saver.save(frame)
                        log.info("final evidence saved → %s", path)

                    break
            else:
                if rover_streak > 0:
                    log.debug("[Phase 2b] rover lost, streak reset (was %d)", rover_streak)
                    rover_streak = 0

    cv2.imshow("Fire Detector", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27 or key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
