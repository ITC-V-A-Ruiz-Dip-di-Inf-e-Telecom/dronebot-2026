from ast import Tuple
import config

def full_inside(inner, outer) -> Tuple:
    shift = config.MAX_ROVER_SHIFT
    x1a, y1a, x2a, y2a = inner
    x1b, y1b, x2b, y2b = outer

    return (
        x1a >= x1b - shift and
        y1a >= y1b - shift and
        x2a <= x2b + shift and
        y2a <= y2b + shift
    )

def iou(box1, box2):
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    inter_width = max(0, x2 - x1)
    inter_height = max(0, y2 - y1)
    inter_area = inter_width * inter_height

    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    sum = box1_area + box2_area - inter_area

    if sum == 0:
        return 0

    return inter_area / sum
