"""
main.py  –  Virtual Flowers AR  (mediapipe 0.10.35, Python 3.13)
Run:  python main.py

Controls:  Q/Esc=quit  S=screenshot  H=toggle HUD

Gestures:
  Open hand  -> flowers BLOOM
  Fist       -> flowers WILT
  Pinch      -> scatter petals
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
from mediapipe.tasks.python.vision import HandLandmarkerOptions, HandLandmarker
import urllib.request, os

from gesture_detector import detect_gesture, fingertip_positions
from flower_engine     import FlowerManager

# ── download model if needed ──────────────────────────────────────────────────
MODEL_PATH = "hand_landmarker.task"
MODEL_URL  = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("Downloading hand landmark model (~8 MB)...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Download complete.")

# ── hand connections (21 landmark pairs) ─────────────────────────────────────
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17),
]

# ── build detector ────────────────────────────────────────────────────────────
options = HandLandmarkerOptions(
    base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=mp_vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
detector = HandLandmarker.create_from_options(options)

# ── helpers ───────────────────────────────────────────────────────────────────
def draw_skeleton(frame, landmarks_list):
    h, w = frame.shape[:2]
    for hand_lms in landmarks_list:
        for a, b in HAND_CONNECTIONS:
            ax = int(hand_lms[a].x * w); ay = int(hand_lms[a].y * h)
            bx = int(hand_lms[b].x * w); by = int(hand_lms[b].y * h)
            cv2.line(frame, (ax, ay), (bx, by), (80, 80, 80), 1, cv2.LINE_AA)
        for lm in hand_lms:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 3, (200, 200, 200), -1, cv2.LINE_AA)

GESTURE_COLOR = {
    "OPEN"   : (80,  210,  80),
    "CLOSED" : (60,  60,  200),
    "PINCH"  : (50,  200, 255),
    "NEUTRAL": (160, 160, 160),
}
GESTURE_LABEL = {
    "OPEN"   : "Open - Blooming!",
    "CLOSED" : "Fist  - Wilting",
    "PINCH"  : "Pinch - Scatter!",
    "NEUTRAL": "Neutral",
}

def draw_hud(frame, gestures, show_hud):
    if not show_hud:
        return
    h, w = frame.shape[:2]
    for i, g in enumerate(gestures):
        label = f"Hand {i+1}: {GESTURE_LABEL.get(g, g)}"
        color = GESTURE_COLOR.get(g, (200, 200, 200))
        cv2.putText(frame, label, (12, 36 + i*28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2, cv2.LINE_AA)
    hints = ["Q=Quit", "S=Screenshot", "H=HUD"]
    for j, hint in enumerate(hints):
        cv2.putText(frame, hint, (w-130, h-14-j*20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (130,130,130), 1, cv2.LINE_AA)

def draw_title(frame):
    w = frame.shape[1]
    cv2.putText(frame, "Virtual Flowers AR", (w//2-130, 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (220,180,255), 2, cv2.LINE_AA)

# ── main loop ─────────────────────────────────────────────────────────────────
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    manager  = FlowerManager()
    show_hud = True
    frame_id = 0

    print("\n  Virtual Flowers AR")
    print("  Open hand -> BLOOM")
    print("  Fist      -> WILT")
    print("  Pinch     -> SCATTER\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        h, w  = frame.shape[:2]

        rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = detector.detect_for_video(mp_img, frame_id)

        all_tips     = []
        all_gestures = []

        if result.hand_landmarks:
            draw_skeleton(frame, result.hand_landmarks)
            for hand_lms in result.hand_landmarks:
                gesture = detect_gesture(hand_lms)
                tips    = fingertip_positions(hand_lms, w, h)
                all_tips.append(tips)
                all_gestures.append(gesture)

        manager.update(frame, all_tips, all_gestures)
        draw_title(frame)
        draw_hud(frame, all_gestures, show_hud)

        cv2.imshow("Virtual Flowers AR  -  Q to quit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break
        elif key == ord('s'):
            fname = f"screenshot_{frame_id}.png"
            cv2.imwrite(fname, frame)
            print(f"Saved {fname}")
        elif key == ord('h'):
            show_hud = not show_hud

        frame_id += 1

    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("Goodbye!")

if __name__ == "__main__":
    main()