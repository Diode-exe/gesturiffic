"""Calculate hand landmarks using MediaPipe Tasks and control mouse with pyautogui.
This version uses the new MediaPipe Tasks API, which has a different structure than the older
Solutions API. Make sure to download the hand_landmarker.task file
from Google's documentation and place it in the same directory as this script."""

import math
import time
import cv2
import mediapipe as mp
import pyautogui

# ------------------------------------
# Mediapipe Tasks Setup
# ------------------------------------
# Download hand_landmarker.task from Google's documentation
MODEL_PATH = 'hand_landmarker.task'

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Create HandLandmarker instance
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=MODEL_PATH),
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
    """Normalize a value from HAND_MIN-HAND_MAX to 0-1"""
    return (v - HAND_MIN) / (HAND_MAX - HAND_MIN)

def ease(x):
    """Ease function for smooth cursor movement"""
    return x * x * x * (x * (x * 6 - 15) + 10)

def pinch_distance(landmarks, a, b):
    """Calculate distance between two landmarks"""
    ax, ay = landmarks[a].x, landmarks[a].y
    bx, by = landmarks[b].x, landmarks[b].y
    return math.hypot(bx - ax, by - ay)

def pinch_index(lm):
    """Detect if index finger is pinching (tip to thumb)"""
    return pinch_distance(lm, 4, 8) < 0.08
def pinch_middle(lm):
    """Detect if middle finger is pinching (tip to thumb)"""
    return pinch_distance(lm, 4, 12) < 0.08
def pinch_pinky(lm):
    """Detect if pinky finger is pinching (tip to thumb)"""
    return pinch_distance(lm, 4, 20) < 0.08

# ------------------------------------
# State
# ------------------------------------
prev_x, prev_y = 0, 0
SMOOTH = 0.25
INDEX_LAST = MIDDLE_LAST = PINKY_LAST = False
LAST_RIGHT_CLICK = 0
RIGHT_DELAY = 0.3

# ------------------------------------
# Camera
# ------------------------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 896)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 504)

print("Welcome to Gesturiffic (Tasks Edition)")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

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

        cur_x = prev_x + (target_x - prev_x) * SMOOTH
        cur_y = prev_y + (target_y - prev_y) * SMOOTH

        pyautogui.moveTo(cur_x, cur_y)
        prev_x, prev_y = cur_x, cur_y

        # ------------------------------------
        # Gestures
        # ------------------------------------
        idx_now = pinch_index(hand_lms)
        mid_now = pinch_middle(hand_lms)
        pinky_now = pinch_pinky(hand_lms)

        if idx_now and not INDEX_LAST:
            pyautogui.click()
            print("Click")

        if mid_now and not MIDDLE_LAST:
            pyautogui.mouseDown()
            print("Drag start")
        elif not mid_now and MIDDLE_LAST:
            pyautogui.mouseUp()
            print("Drag end")

        now = time.time()
        if pinky_now and not PINKY_LAST and now - LAST_RIGHT_CLICK >= RIGHT_DELAY:
            pyautogui.rightClick()
            LAST_RIGHT_CLICK = now
            print("Right click")

        INDEX_LAST, MIDDLE_LAST, PINKY_LAST = idx_now, mid_now, pinky_now

    cv2.imshow("Gesturiffic", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

landmarker.close()
cap.release()
cv2.destroyAllWindows()
