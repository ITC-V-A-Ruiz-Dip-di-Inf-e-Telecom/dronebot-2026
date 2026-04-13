VIDEO_SOURCE = "/dev/video10"

# Phase 1
YOLO_MODEL_PATH = "../../models/best.pt"
YOLO_CONFIDENCE = 0.70
FIRE_CONFIR_FRAMES = 7
MIN_FIRE_AREA = 20000 # Min num of pixels
MAX_FIRE_SHIFT = 250 # Max pixel shift for the fire area betwen frames

# Phase 2
ARUCO_DICTIONARY_NAME = "DICT_4X4_50"
ARUCO_ID = 10
ROVER_CONFIRM_FRAMES = 5
MAX_ROVER_SHIFT = 30
MIN_OVERLAP_AREA = 0.9

SAVE_EVIDENCE = True
