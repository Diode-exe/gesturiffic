import cv2
import mediapipe as mp
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
)
volume = cast(interface, POINTER(IAudioEndpointVolume))

current = volume.GetMasterVolumeLevelScalar()
print(current)

def increaseVolume():
    volume.SetMasterVolumeLevelScalar(min(current + 0.1, 1.0), None)

def decreaseVolume():
    volume.SetMasterVolumeLevelScalar(max(current - 0.1, 0.0), None)

def muteVolume():
    volume.SetMasterVolumeLevelScalar(0, None)

def is_fist(handLms):
    # For fingers except thumb
    fingers = [(8,6), (12,10), (16,14), (20,18)]
    for tip, pip in fingers:
        if handLms.landmark[tip].y < handLms.landmark[pip].y:
            # finger is extended
            return False
    # Optionally check thumb across palm
    if handLms.landmark[4].x > handLms.landmark[3].x:
        return False
    return True


cap = cv2.VideoCapture(0)
# outside loop
last_gesture = None

while True:
    ret, frame = cap.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    gesture = None  # current gesture

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)

            if is_fist(handLms):
                gesture = "fist"
            elif handLms.landmark[8].y < handLms.landmark[6].y:
                gesture = "index_up"
            elif handLms.landmark[20].y < handLms.landmark[17].y:
                gesture = "pinky_up"
            # add more gestures if needed

    # trigger action only on change
    if gesture != last_gesture:
        if gesture == "fist":
            print("fist")
            muteVolume()
        elif gesture == "index_up":
            increaseVolume()
            print("index")
        elif gesture == "pinky_up":
            decreaseVolume()
            print("pinky")

    last_gesture = gesture

    cv2.imshow("Feed", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
