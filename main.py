import cv2
import mediapipe as mp
import pyautogui
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import time

last_click_time = 0
double_click_delay = 0.3

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

def isPinkyThumb(handLMS, threshold=0.05):
    # thumb tip (4) pinky tip (20)
    x1, y1 = handLms.landmark[4].x, handLms.landmark[4].y
    x2, y2 = handLms.landmark[20].x, handLms.landmark[20].y
    distance = math.hypot(x2 - x1, y2 - y1)
    return distance < threshold

# Camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 854)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# State tracking
last_gesture = None
prev_cursor_x, prev_cursor_y = 0, 0
smoothing = 0.2
pinched_last_frame = False

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture = None
    cursor_x, cursor_y = prev_cursor_x, prev_cursor_y
    pinch_now = False
    pinky_thumb_now = False

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

            # ---- Cursor mapping ----
            x_scale = 2.0
            y_scale = 2.0

            x_norm = handLms.landmark[8].x - 0.5
            y_norm = handLms.landmark[8].y - 0.5

            x_mapped = min(max(x_norm * x_scale + 0.5, 0), 1)
            y_mapped = min(max(y_norm * y_scale + 0.5, 0), 1)

            target_x = x_mapped * screen_width
            target_y = y_mapped * screen_height
            cursor_x = prev_cursor_x + (target_x - prev_cursor_x) * smoothing
            cursor_y = prev_cursor_y + (target_y - prev_cursor_y) * smoothing

            # ---- Pinch detection ----
            if is_pinch(handLms):
                pinch_now = True
            if isPinkyThumb(handLms):
                pinky_thumb_now = True

    # ---- Handle pinch click ----
    if pinch_now and not pinched_last_frame:
        now = time.time()
        if now - last_click_time < double_click_delay:
            pyautogui.doubleClick()
            print("Double Click!")
            last_click_time = 0
        else:
            pyautogui.click()
            print("Single Click!")
            last_click_time = now

    pinched_last_frame = pinch_now

    if pinky_thumb_now and not pinky_thumb_last_frame:
        pyautogui.rightClick()
        print("Right click!")

    pinky_thumb_last_frame = pinky_thumb_now

    # Move cursor every frame
    pyautogui.moveTo(cursor_x, cursor_y)
    prev_cursor_x, prev_cursor_y = cursor_x, cursor_y

    # ---- Always show frame ----
    cv2.imshow("Feed", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()
