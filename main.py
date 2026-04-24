"""Calculate hand landmarks using MediaPipe Tasks and control mouse with pyautogui.
This version uses the new MediaPipe Tasks API, which has a different structure than the older
Solutions API. Make sure to download the hand_landmarker.task file
from Google's documentation and place it in the same directory as this script."""

import math
import time
import cv2
import mediapipe as mp
import pyautogui
from version import Version

# ------------------------------------
# Mediapipe Tasks Setup
# ------------------------------------
# Download hand_landmarker.task from Google's documentation
class HandTracker:
    """A simple class to hold the hand tracking model and related options."""
    def __init__(self, model_path="hand_landmarker.task"):
        self.model_path = model_path
        self.ax, self.ay, self.bx, self.by = 0, 0, 0, 0
        self.prev_x, self.prev_y = 0, 0
        self.SMOOTH = 0.25
        self.INDEX_LAST = self.MIDDLE_LAST = self.PINKY_LAST = False
        self.LAST_RIGHT_CLICK = 0
        self.RIGHT_DELAY = 0.3
        self.SCREEN_W, self.SCREEN_H = pyautogui.size()
        self.CAP_W, self.CAP_H = self.SCREEN_W // 2, self.SCREEN_H // 2

        self.base_options = mp.tasks.BaseOptions
        self.hand_landmarker = mp.tasks.vision.HandLandmarker
        self.hand_landmarker_options = mp.tasks.vision.HandLandmarkerOptions
        self.vision_running_mode = mp.tasks.vision.RunningMode

        # Create HandLandmarker instance
        options = self.hand_landmarker_options(
            base_options=self.base_options(model_asset_path=self.model_path),
            running_mode=self.vision_running_mode.VIDEO, # Using VIDEO mode for sync loop
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.landmarker = self.hand_landmarker.create_from_options(options)

        self.hand_min = 0.05
        self.hand_max = 0.95

        pyautogui.FAILSAFE = False

    def pinch_index(self, lm):
        """Detect if index finger is pinching (tip to thumb)"""
        return self.pinch_distance(lm, 4, 8) < 0.08
    def pinch_middle(self, lm):
        """Detect if middle finger is pinching (tip to thumb)"""
        return self.pinch_distance(lm, 4, 12) < 0.08
    def pinch_pinky(self, lm):
        """Detect if pinky finger is pinching (tip to thumb)"""
        return self.pinch_distance(lm, 4, 20) < 0.08

    def normalize(self, v):
        """Normalize a value from hand_min-hand_max to 0-1"""
        return (v - self.hand_min) / (self.hand_max - self.hand_min)

    def ease(self, x):
        """Ease function for smooth cursor movement"""
        return x * x * x * (x * (x * 6 - 15) + 10)

    def pinch_distance(self, landmarks, a, b):
        """Calculate distance between two landmarks"""
        self.ax, self.ay = landmarks[a].x, landmarks[a].y
        self.bx, self.by = landmarks[b].x, landmarks[b].y
        return math.hypot(self.bx - self.ax, self.by - self.ay)

class VideoCapture:
    """A simple wrapper around cv2.VideoCapture to set resolution."""
    def __init__(self):
        versioner = Version()
        self.tracking = HandTracker()
        self.VERSION = versioner.version
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.tracking.CAP_W)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.tracking.CAP_H)

    def video_loop(self):
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # MediaPipe Tasks requires an mp.Image object
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            # Calculate timestamp in ms
            timestamp_ms = int(time.time() * 1000)

            # Process frame
            results = self.tracking.landmarker.detect_for_video(mp_image, timestamp_ms)

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

                nx = self.tracking.ease(min(max(self.tracking.normalize(raw_x), 0), 1))
                ny = self.tracking.ease(min(max(self.tracking.normalize(raw_y), 0), 1))

                target_x = nx * self.tracking.SCREEN_W
                target_y = ny * self.tracking.SCREEN_H

                cur_x = self.tracking.prev_x + (target_x - self.tracking.prev_x) * self.tracking.SMOOTH
                cur_y = self.tracking.prev_y + (target_y - self.tracking.prev_y) * self.tracking.SMOOTH

                pyautogui.moveTo(cur_x, cur_y)
                self.tracking.prev_x, self.tracking.prev_y = cur_x, cur_y

                # ------------------------------------
                # Gestures
                # ------------------------------------
                idx_now = self.tracking.pinch_index(hand_lms)
                mid_now = self.tracking.pinch_middle(hand_lms)
                pinky_now = self.tracking.pinch_pinky(hand_lms)

                if idx_now and not self.tracking.INDEX_LAST:
                    pyautogui.click()
                    print("Click")

                if mid_now and not self.tracking.MIDDLE_LAST:
                    pyautogui.mouseDown()
                    print("Drag start")
                elif not mid_now and self.tracking.MIDDLE_LAST:
                    pyautogui.mouseUp()
                    print("Drag end")

                now = time.time()
                if pinky_now and not self.tracking.PINKY_LAST and now - self.tracking.LAST_RIGHT_CLICK >= self.tracking.RIGHT_DELAY:
                    pyautogui.rightClick()
                    self.tracking.LAST_RIGHT_CLICK = now
                    print("Right click")

                self.tracking.INDEX_LAST, self.tracking.MIDDLE_LAST, self.tracking.PINKY_LAST = idx_now, mid_now, pinky_now

            cv2.imshow(f"Gesturiffic {self.VERSION}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.tracking.landmarker.close()
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    capture = VideoCapture()
    print(f"Welcome to Gesturiffic {capture.VERSION}!")
    print("Press 'q' to quit.")
    capture.video_loop()
