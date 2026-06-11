"""
gesture_detector.py — works with mediapipe 0.10.30+ new API
"""
import math

WRIST      = 0
THUMB_TIP  = 4
INDEX_MCP  = 5;  INDEX_TIP  = 8
MIDDLE_MCP = 9;  MIDDLE_TIP = 12
RING_MCP   = 13; RING_TIP   = 16
PINKY_MCP  = 17; PINKY_TIP  = 20

def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def _finger_extended(lm, tip_idx, mcp_idx):
    return _dist(lm[tip_idx], lm[WRIST]) > _dist(lm[mcp_idx], lm[WRIST]) * 1.05

def detect_gesture(hand_landmarks) -> str:
    lm = hand_landmarks
    index_ext  = _finger_extended(lm, INDEX_TIP,  INDEX_MCP)
    middle_ext = _finger_extended(lm, MIDDLE_TIP, MIDDLE_MCP)
    ring_ext   = _finger_extended(lm, RING_TIP,   RING_MCP)
    pinky_ext  = _finger_extended(lm, PINKY_TIP,  PINKY_MCP)
    pinch_dist = _dist(lm[THUMB_TIP], lm[INDEX_TIP])
    is_pinch   = pinch_dist < 0.06 and not middle_ext
    if is_pinch:
        return "PINCH"
    fingers_up = sum([index_ext, middle_ext, ring_ext, pinky_ext])
    if fingers_up >= 3:
        return "OPEN"
    elif fingers_up == 0:
        return "CLOSED"
    return "NEUTRAL"

def fingertip_positions(hand_landmarks, frame_w, frame_h) -> list:
    tips = [THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]
    return [(int(hand_landmarks[t].x * frame_w), int(hand_landmarks[t].y * frame_h)) for t in tips]