import cv2
import mediapipe as mp
import numpy as np

class FingerDetector:
    def __init__(self, static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5):
        """
        Initialize MediaPipe Hands.
        """
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence
        )
        # Index tip, Middle tip, Ring tip, Pinky tip (Skipping Thumb: 4)
        self.fingertip_ids = [8, 12, 16, 20]

    def detect(self, img):
        """
        Detect fingertips in the image.
        Args:
            img: BGR image (numpy array)
        Returns:
            List of (x, y) coordinates for all detected fingertips (Left hand only).
        """
        # Validate input image dimensions and handle conversions
        if img.ndim == 2:
            # Grayscale to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        elif img.ndim == 3 and img.shape[2] == 3:
            # BGR to RGB (Standard OpenCV)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        elif img.ndim == 3 and img.shape[2] == 4:
            # BGRA to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        else:
            # Unexpected format, attempt to use as-is (e.g. already RGB) or let MediaPipe handle/fail
            img_rgb = img

        results = self.hands.process(img_rgb)
        fingertips = []

        if results.multi_hand_landmarks and results.multi_handedness:
            h, w, _ = img.shape
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # Filter for Left hand only
                # Note: MediaPipe assumes the input image is mirrored by default if it's a selfie camera.
                # Label "Left" corresponds to the person's left hand.
                label = handedness.classification[0].label
                if label != "Left":
                    continue

                print(f"✋ Left hand detected with {len(hand_landmarks.landmark)} landmarks")
                for idx in self.fingertip_ids:
                    lm = hand_landmarks.landmark[idx]
                    # Convert normalized coordinates to pixel coordinates
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    fingertips.append((cx, cy))
        
        if fingertips:
            print(f"✅ Detected {len(fingertips)} fingertips: {fingertips}")
        
        return fingertips

