import cv2
import mediapipe as mp
import pyautogui
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math

# Mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

pyautogui.FAILSAFE = False

# Screen size
screen_width, screen_height = pyautogui.size()

# Pycaw volume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

def increaseVolume():
    current = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(min(current + 0.05, 1.0), None)

def decreaseVolume():
    current = volume.GetMasterVolumeLevelScalar()
    volume.SetMasterVolumeLevelScalar(max(current - 0.05, 0.0), None)

def muteVolume():
    volume.SetMasterVolumeLevelScalar(0, None)

def is_fist(handLms):
    fingers = [(8,6), (12,10), (16,14), (20,18)]
    for tip, pip in fingers:
        if handLms.landmark[tip].y < handLms.landmark[pip].y:
            return False
    if handLms.landmark[4].x > handLms.landmark[3].x:
        return False
    return True

def is_pinch(handLms, threshold=0.05):
    # Distance between thumb tip (4) and index tip (8)
    x1, y1 = handLms.landmark[4].x, handLms.landmark[4].y
    x2, y2 = handLms.landmark[8].x, handLms.landmark[8].y
    distance = math.hypot(x2 - x1, y2 - y1)
    return distance < threshold

# Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# State tracking
last_gesture = None
prev_cursor_x, prev_cursor_y = 0, 0
smoothing = 0.2
pinched_last_frame = False

while True:
    ret, frame = cap.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture = None
    cursor_x, cursor_y = prev_cursor_x, prev_cursor_y
    pinch_now = False

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

            # ---- Cursor mapping ----
            target_x = handLms.landmark[8].x * screen_width
            target_y = handLms.landmark[20].y * screen_height
            cursor_x = prev_cursor_x + (target_x - prev_cursor_x) * smoothing
            cursor_y = prev_cursor_y + (target_y - prev_cursor_y) * smoothing

            # ---- Pinch detection ----
            if is_pinch(handLms):
                pinch_now = True

    # ---- Handle pinch click ----
    if pinch_now and not pinched_last_frame:
        pyautogui.click()
        print("Click!")

    pinched_last_frame = pinch_now

    # Move cursor every frame
    pyautogui.moveTo(cursor_x, cursor_y)
    prev_cursor_x, prev_cursor_y = cursor_x, cursor_y

    # Show camera
    cv2.imshow("Feed", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
