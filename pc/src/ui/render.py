import cv2
from cv2.detail import PairwiseSeamFinder

class Render:
    def __init__(self) -> None:
        # Colors
        self.FIRE = (0, 69, 255)
        self.ALLERT = (0, 0, 255)
        self.GREY = (40, 40, 40)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.ORANGE = (0, 165, 255)

    def draw(self, frame, detections):

        output = frame.copy()

        for detec in detections:
            x1, y1, x2, y2 = detec["box"]
            confidence = detec["confidence"]

            # Filled background for better visibility
            overlay = output.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), self.FIRE, -1)
            cv2.addWeighted(overlay, 0.2, output, 0.8, 0, output)

            # Bounding box
            cv2.rectangle(output, (x1, y1), (x2, y2), self.FIRE, 3)
            cv2.rectangle(output, (x1-2, y1-2), (x2+2, y2+2), (0, 100, 255), 1)

            # Fire lable with background
            lable = f"FIRE {confidence*100:.1f}%"
            (lable_w, lable_h), baseline = cv2.getTextSize(
                lable, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3
            )

            # Fire lable box
            cv2.rectangle(
                output,
                (x1, y1 - lable_h - baseline - 15),
                (x1 + lable_w + 15, y1),
                self.FIRE,
                -1
            )

            # Lable text in box
            cv2.putText(
                output,
                lable,
                (x1 + 7, y1 - 12),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                self.WHITE,
                3,
                cv2.LINE_AA
            )

        return output

    def draw_rover(self, frame, rover_box, status="detected"):
        output = frame.copy()
        x1, y1, x2, y2 = rover_box

        if status == "contained":
            box_color = self.GREEN
            label_bg_color = self.GREEN
            label_text = "ROVER - CONTAINED"
        elif status == "not_contained":
            box_color = self.ALLERT
            label_bg_color = self.ALLERT
            label_text = "ROVER - NOT CONTAINED"
        else:  # waiting for fire box
            box_color = (0, 255, 255)
            label_bg_color = (0, 180, 180)
            label_text = "ROVER - DETECTED"

        overlay = output.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), box_color, -1)
        cv2.addWeighted(overlay, 0.15, output, 0.85, 0, output)

        cv2.rectangle(output, (x1, y1), (x2, y2), box_color, 3)

        accent_color = tuple(int(c * 0.7) for c in box_color)  # Darker shade
        cv2.rectangle(output, (x1-2, y1-2), (x2+2, y2+2), accent_color, 1)

        (label_w, label_h), baseline = cv2.getTextSize(
            label_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 3
        )

        # Label box
        cv2.rectangle(
            output,
            (x1, y1 - label_h - baseline - 15),
            (x1 + label_w + 15, y1),
            label_bg_color,
            -1
        )

        # Label text
        cv2.putText(
            output,
            label_text,
            (x1 + 7, y1 - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            self.WHITE,
            3,
            cv2.LINE_AA
        )

        return output

    def draw_info(self, frame, fps, total_detections, device, fire_alert=False):
        h, w = frame.shape[:2]

        # Semi trandparent background
        panel_heigh = 140
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, panel_heigh), self.GREY, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Device (GPU/CPU)
        device_text = "GPU" if device == "cuda" else "CPU"
        device_color = self.GREEN if device == "cuda" else self.ORANGE
        cv2.putText(
            frame,
            f"[{device_text}]",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            device_color,
            2,
            cv2.LINE_AA
        )

        # FPS counter with color range
        fps_color = self.ORANGE if fps > 20 else (0 ,165, 255) if fps > 10 else self.ALLERT
        cv2.putText(
            frame,
            f"{fps:.1f}",
            (20, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            2.5,
            fps_color,
            4,
            cv2.LINE_AA
        )

        # FPS lable
        cv2.putText(
            frame,
            "FPS",
            (180, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            self.WHITE,
            2,
            cv2.LINE_AA
        )

        # Total detections
        detections_text = f"Confirmed Fires: {total_detections}"
        text_size = cv2.getTextSize(detections_text, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)[0]
        cv2.putText(
            frame,
            detections_text,
            (w - text_size[0] - 20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            self.WHITE,
            2,
            cv2.LINE_AA
        )

        # Fire banner
        if fire_alert:
            alert_h = 80
            alert_overlay = frame.copy()
            cv2.rectangle(alert_overlay, (0, h - alert_h), (w, h), self.ALLERT, -1)
            cv2.addWeighted(alert_overlay, 0.6, frame, 0.4, 0, frame)

            # Pulsing effect
            text = "!!! FIRE DETECTED !!!"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            text_x = (w - text_size[0]) // 2
            text_y = h - alert_h // 2 + text_size[1] // 2

            cv2.putText(
                frame,
                text,
                (text_x, text_y),
                cv2.FONT_HERSHEY_DUPLEX,
                1.5,
                self.WHITE,
                3,
                cv2.LINE_AA
            )

        return frame
