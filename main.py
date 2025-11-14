import cv2
import mediapipe as mp
import pyautogui
import math
import time

# ------------------------------------
# Mediapipe setup
# ------------------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

pyautogui.FAILSAFE = False
screen_w, screen_h = pyautogui.size()

# ------------------------------------
# Hand normalization range
# ------------------------------------
# These values define the "usable" portion of the camera image.
# You can widen/narrow these if needed.
HAND_MIN = 0.15
HAND_MAX = 0.85

def normalize(v):
    """Map camera range (HAND_MIN–HAND_MAX) to (0–1)."""
    return (v - HAND_MIN) / (HAND_MAX - HAND_MIN)

# ------------------------------------
# Pinch detection helpers
# ------------------------------------
def pinch_distance(hand, a, b):
    ax, ay = hand.landmark[a].x, hand.landmark[a].y
    bx, by = hand.landmark[b].x, hand.landmark[b].y
    return math.hypot(bx - ax, by - ay)

def pinch_index(hand): return pinch_distance(hand, 4, 8) < 0.08
def pinch_middle(hand): return pinch_distance(hand, 4, 12) < 0.08
def pinch_pinky(hand): return pinch_distance(hand, 4, 20) < 0.08

# ------------------------------------
# State
# ------------------------------------
prev_x, prev_y = 0, 0
smooth = 0.25

index_last = False
middle_last = False
pinky_last = False

last_right_click = 0
right_delay = 0.3

# ------------------------------------
# Camera
# ------------------------------------
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 854)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Welcome to Gesturiffic")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

        # ------------------------------------
        # Finger position -> screen position
        # ------------------------------------
        raw_x = hand.landmark[8].x
        raw_y = hand.landmark[8].y

        # Normalize into 0–1 range
        nx = min(max(normalize(raw_x), 0), 1)
        ny = min(max(normalize(raw_y), 0), 1)

        target_x = nx * screen_w
        target_y = ny * screen_h

        # Smooth movement
        cur_x = prev_x + (target_x - prev_x) * smooth
        cur_y = prev_y + (target_y - prev_y) * smooth

        pyautogui.moveTo(cur_x, cur_y)
        prev_x, prev_y = cur_x, cur_y

        # ------------------------------------
        # Gestures
        # ------------------------------------
        idx_now = pinch_index(hand)
        mid_now = pinch_middle(hand)
        pinky_now = pinch_pinky(hand)

        # left click
        if idx_now and not index_last:
            pyautogui.click()
            print("Click")

        # drag
        if mid_now and not middle_last:
            pyautogui.mouseDown()
            print("Drag start")

        if not mid_now and middle_last:
            pyautogui.mouseUp()
            print("Drag end")

        # right click
        now = time.time()
        if pinky_now and not pinky_last and now - last_right_click >= right_delay:
            pyautogui.rightClick()
            last_right_click = now
            print("Right click")

        index_last = idx_now
        middle_last = mid_now
        pinky_last = pinky_now

    # show frame
    cv2.imshow("Gesturiffic", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
