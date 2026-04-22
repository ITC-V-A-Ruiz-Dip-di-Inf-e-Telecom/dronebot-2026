VIDEO_SOURCE = "/dev/video10"

# Phase 1 fire detection
YOLO_MODEL_PATH = "../../models/best.pt"
YOLO_CONFIDENCE = 0.85
FIRE_CONFIR_FRAMES = 7
MIN_FIRE_AREA = 10000 # minimum pixel area for a valid fire detection
MAX_FIRE_SHIFT = 150

# Phase 2 rover tracking & containment
ARUCO_DICTIONARY_NAME = "DICT_4X4_50"
ARUCO_ID = 10
FIRE_LOCK_FRAMES = 20 # consecutive stable frames to re-lock the fire circle
ROVER_CONFIRM_FRAMES = 5
MAX_ROVER_SHIFT = 15 # pixel tolerance added to the fire circle radius

SAVE_EVIDENCE = True

# Raspberry Pi rover server
RASPBERRY_PI_URL = "http://192.168.203.132:5000"
