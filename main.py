import cv2
import mediapipe as mp
import pyautogui
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import math
import time

# -------------------------
# Mediapipe
# -------------------------
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

pyautogui.FAILSAFE = False
screen_width, screen_height = pyautogui.size()

# -------------------------
# Audio volume (pycaw)
# -------------------------
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))


# -------------------------
# Gesture detection helpers
# -------------------------
def pinch_distance(handLms, a, b):
    x1, y1 = handLms.landmark[a].x, handLms.landmark[a].y
    x2, y2 = handLms.landmark[b].x, handLms.landmark[b].y
    return math.hypot(x2 - x1, y2 - y1)

def pinch_index(handLms, th=0.05):
    return pinch_distance(handLms, 4, 8) < th

def pinch_middle(handLms, th=0.05):
    return pinch_distance(handLms, 4, 12) < th

def pinch_pinky(handLms, th=0.05):
    return pinch_distance(handLms, 4, 20) < th


# -------------------------
# State variables
# -------------------------
prev_x, prev_y = 0, 0
smooth = 0.2

index_last = False
middle_last = False
pinky_last = False

last_right_click = 0
right_click_delay = 0.3


# -------------------------
# Camera
# -------------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 854)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        handLms = results.multi_hand_landmarks[0]
        mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

        # -------------------------
        # Cursor smoothing
        # -------------------------
        x_norm = handLms.landmark[8].x - 0.5
        y_norm = handLms.landmark[8].y - 0.5

        x_map = min(max(x_norm * 2 + 0.5, 0), 1)
        y_map = min(max(y_norm * 2 + 0.5, 0), 1)

        target_x = x_map * screen_width
        target_y = y_map * screen_height

        cur_x = prev_x + (target_x - prev_x) * smooth
        cur_y = prev_y + (target_y - prev_y) * smooth

        pyautogui.moveTo(cur_x, cur_y)
        prev_x, prev_y = cur_x, cur_y

        # -------------------------
        # Gesture states
        # -------------------------
        idx_now = pinch_index(handLms)
        mid_now = pinch_middle(handLms)
        pinky_now = pinch_pinky(handLms)

        # -------------------------
        # Index pinch -> single click
        # -------------------------
        if idx_now and not index_last:
            pyautogui.click()
            print("Single click")

        # -------------------------
        # Middle pinch -> hold & drag
        # -------------------------
        if mid_now and not middle_last:
            pyautogui.mouseDown()
            print("Hold start")

        if not mid_now and middle_last:
            pyautogui.mouseUp()
            print("Hold end")

        # -------------------------
        # Pinky pinch -> right click (debounced)
        # -------------------------
        now = time.time()
        if pinky_now and not pinky_last:
            if now - last_right_click >= right_click_delay:
                pyautogui.rightClick()
                last_right_click = now
                print("Right click")

        index_last = idx_now
        middle_last = mid_now
        pinky_last = pinky_now

    cv2.imshow("Feed", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
