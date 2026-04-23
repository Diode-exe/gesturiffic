import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import pyautogui
import math
import time

# ------------------------------------
# Mediapipe Tasks Setup
# ------------------------------------
# Download hand_landmarker.task from Google's documentation
model_path = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Create HandLandmarker instance
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO, # Using VIDEO mode for sync loop
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

landmarker = HandLandmarker.create_from_options(options)

pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()

# ------------------------------------
# Hand normalization & Helpers
# ------------------------------------
HAND_MIN = 0.05
HAND_MAX = 0.95

def normalize(v):
    return (v - HAND_MIN) / (HAND_MAX - HAND_MIN)

def ease(x):
    return x * x * x * (x * (x * 6 - 15) + 10)

def pinch_distance(landmarks, a, b):
    ax, ay = landmarks[a].x, landmarks[a].y
    bx, by = landmarks[b].x, landmarks[b].y
    return math.hypot(bx - ax, by - ay)

def pinch_index(lm): return pinch_distance(lm, 4, 8) < 0.08
def pinch_middle(lm): return pinch_distance(lm, 4, 12) < 0.08
def pinch_pinky(lm): return pinch_distance(lm, 4, 20) < 0.08

# ------------------------------------
# State
# ------------------------------------
prev_x, prev_y = 0, 0
smooth = 0.25
index_last = middle_last = pinky_last = False
last_right_click = 0
right_delay = 0.3

# ------------------------------------
# Camera
# ------------------------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 896)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 504)

print("Welcome to Gesturiffic (Tasks Edition)")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # MediaPipe Tasks requires an mp.Image object
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    # Calculate timestamp in ms
    timestamp_ms = int(time.time() * 1000)

    # Process frame
    results = landmarker.detect_for_video(mp_image, timestamp_ms)

    if results.hand_landmarks:
        # Results format changed slightly: it's a list of lists of landmarks
        hand_lms = results.hand_landmarks[0]

        # Drawing (Requires converting back to old LandmarkList for legacy drawer)
        # Or just manually draw. For now, let's stick to the raw logic.

        # ------------------------------------
        # Finger position -> screen position
        # ------------------------------------
        # Landmark 8 = Index Tip
        raw_x = hand_lms[8].x
        raw_y = hand_lms[8].y

        nx = ease(min(max(normalize(raw_x), 0), 1))
        ny = ease(min(max(normalize(raw_y), 0), 1))

        target_x = nx * screen_w
        target_y = ny * screen_h

        cur_x = prev_x + (target_x - prev_x) * smooth
        cur_y = prev_y + (target_y - prev_y) * smooth

        pyautogui.moveTo(cur_x, cur_y)
        prev_x, prev_y = cur_x, cur_y

        # ------------------------------------
        # Gestures
        # ------------------------------------
        idx_now = pinch_index(hand_lms)
        mid_now = pinch_middle(hand_lms)
        pinky_now = pinch_pinky(hand_lms)

        if idx_now and not index_last:
            pyautogui.click()
            print("Click")

        if mid_now and not middle_last:
            pyautogui.mouseDown()
            print("Drag start")
        elif not mid_now and middle_last:
            pyautogui.mouseUp()
            print("Drag end")

        now = time.time()
        if pinky_now and not pinky_last and now - last_right_click >= right_delay:
            pyautogui.rightClick()
            last_right_click = now
            print("Right click")

        index_last, middle_last, pinky_last = idx_now, mid_now, pinky_now

    cv2.imshow("Gesturiffic", frame)
    if cv2.waitKey(1) & 0xFF == 27: break

landmarker.close()
cap.release()
cv2.destroyAllWindows()