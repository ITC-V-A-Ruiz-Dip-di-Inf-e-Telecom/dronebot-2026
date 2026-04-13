import cv2
import numpy as np
import config

class ARUCODetector:

    def __init__ (self) -> None:
        aruco_dict = getattr(cv2.aruco, config.ARUCO_DICTIONARY_NAME)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict)
        self.parameters = cv2.aruco.DetectorParameters()

    def detect(self, frame):

        corners, ids, _ = cv2.aruco.detectMarkers(
            frame,
            self.aruco_dict,
            parameters=self.parameters
        )

        if ids is None:
            return None

        for i, marker_id in enumerate(ids.flatten()):
            if marker_id == config.ARUCO_ID:
                points = corners[i][0]

                x_min = int(np.min(points[:, 0]))
                y_min = int(np.min(points[:, 1]))
                x_max = int(np.max(points[:, 0]))
                y_max = int(np.max(points[:, 1]))

                return (x_min, y_min, x_max, y_max)

        return None
