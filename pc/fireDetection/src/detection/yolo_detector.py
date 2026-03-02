from ultralytics import YOLO
import numpy
from pathlib import Path
import torch

class Detector:
    def __init__(self, model_path="../../models/best.pt", confidence=0.7) -> None:
        self.confidence_threshold = confidence
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'

        path = Path(__file__).parent / model_path

        if path.exists():
            self.model = YOLO(path)
            self.model.to(self.device)
            print(f"Loaded model from path on device: {self.device}")
            if self.device == 'cuda':
                print(f"GPU: {torch.cuda.get_device_name(0)}")
        else:
            print("Model not loaded, not present at path")
            
    def detect(self, frame):
        result = self.model(frame, conf=self.confidence_threshold, verbose=False)[0]

        detections = []

        if result.boxes is None:
            return detections

        confidences = result.boxes.conf.cpu().numpy()
        boxes = result.boxes.xyxy.cpu().numpy()

        for box, confidence in zip(boxes, confidences):
            x1, y1, x2, y2 = box.astype(int)

            detections.append({
                "box": (x1, y1, x2, y2),
                "confidence": float(confidence)
                })
        
        return detections
