import cv2
import numpy as np
import matplotlib.pyplot as plt
import config

aruco_dict = getattr(cv2.aruco, config.ARUCO_DICTIONARY_NAME)
aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict)

aruco_id = config.ARUCO_ID
aruco_size = 200
aruco_image = cv2.aruco.generateImageMarker(aruco_dict, aruco_id, aruco_size)

cv2.imwrite("aruco_marker.png", aruco_image)
