"""
Finger detection using MediaPipe Hands + Homography Tracking.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import List, Optional, Dict, Any, Tuple

import cv2
import numpy as np

from image import Image
from fretboard_tracker import FretboardTracker, GridSystem

try:
    import mediapipe as mp
except ImportError as e:
    raise ImportError(
        "mediapipe is not installed. Please install it in your venv, e.g.:\n"
        "  pip install mediapipe"
    ) from e


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class ExpectedPosition:
    string: int  # 1 (high E) ... 6 (low E)
    fret: int    # 0=open, 1,2,...


@dataclass
class DetectedFingertip:
    x: int
    y: int
    string: Optional[int] = None
    fret: Optional[int] = None
    tip_id: Optional[int] = None  # MediaPipe landmark index


# ---------------------------------------------------------------------------
# MediaPipe fingertip detector
# ---------------------------------------------------------------------------


class MediaPipeHandDetector:
    """Wrapper around MediaPipe Hands to detect fingertip locations (pixels)."""

    # Only use 4 fingertips relevant for fretting (index, middle, ring, pinky).
    # MediaPipe landmark indices: index=8, middle=12, ring=16, pinky=20.
    TIP_IDS = [8, 12, 16, 20]

    def __init__(
        self,
        static_image_mode: bool = False, # Default to dynamic for tracking
        max_num_hands: int = 2,
        min_detection_confidence: float = 0.5,
    ) -> None:
        self._hands = mp.solutions.hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
        )

    def detect_fingertips(self, img_bgr: np.ndarray) -> List[DetectedFingertip]:
        """Return fingertip pixel coordinates in the given BGR image."""
        h, w = img_bgr.shape[:2]
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(img_rgb)

        tips: List[DetectedFingertip] = []
        if not results.multi_hand_landmarks:
            return tips

        for hand_landmarks in results.multi_hand_landmarks:
            for tip_id in self.TIP_IDS:
                lm = hand_landmarks.landmark[tip_id]
                x_px = int(lm.x * w)
                y_px = int(lm.y * h)
                tips.append(DetectedFingertip(x=x_px, y=y_px, tip_id=tip_id))

        return tips


# ---------------------------------------------------------------------------
# High-level analyzer
# ---------------------------------------------------------------------------


class FingerAnalyzer:
    """
    High level utility using Homography Tracking:
    - Tracks fretboard using feature matching against a reference image
    - Maps fingertips to reference grid
    """

    def __init__(self) -> None:
        self.detector = MediaPipeHandDetector(static_image_mode=True) # True for single images, False for video
        
        # Auto-load reference data if exists
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ref_img_path = os.path.join(base_dir, "reference_neck.jpg")
        grid_json_path = os.path.join(base_dir, "reference_grid.json")
        
        self.tracker = None
        self.grid_system = None
        
        if os.path.exists(ref_img_path) and os.path.exists(grid_json_path):
            print(f"✅ Loading Reference System: {ref_img_path}")
            try:
                self.tracker = FretboardTracker(ref_img_path)
                self.grid_system = GridSystem()
                self.grid_system.load_from_json(grid_json_path)
            except Exception as e:
                print(f"⚠️ Failed to init tracker: {e}")
        else:
            print("⚠️ Reference files not found. Please run generate_reference_grid.py first.")

    def analyze(
        self,
        full_bgr: np.ndarray,
        roi_bgr: Optional[np.ndarray] = None, # Kept for API compatibility
        roi_offset: Tuple[int, int] = (0, 0), # Kept for API compatibility
        expected_positions: Optional[List[ExpectedPosition]] = None,
    ) -> Dict[str, Any]:
        
        # 1) Detect fingertips (pixels) on the full frame
        # Note: For tracking, we prefer working on the Full Frame directly.
        # If full_bgr is rotated, that's fine as long as Reference is also rotated.
        raw_tips = self.detector.detect_fingertips(full_bgr)
        
        mapped_tips: List[DetectedFingertip] = []
        current_H = None
        
        # 2) Track Grid
        if self.tracker and self.grid_system:
            H, mask = self.tracker.process_frame(full_bgr)
            current_H = H
            
            if H is not None:
                # Map tips to reference
                for tip in raw_tips:
                    # Map (x,y) -> (x_ref, y_ref)
                    ref_pt = self.tracker.map_point_to_reference(tip.x, tip.y, H)
                    
                    s_idx = None
                    f_idx = None
                    
                    if ref_pt:
                        rx, ry = ref_pt
                        s_idx = self.grid_system.get_string_index(rx, ry)
                        f_idx = self.grid_system.get_fret_index(rx, ry)
                        
                    mapped_tips.append(
                        DetectedFingertip(
                            x=tip.x, y=tip.y, string=s_idx, fret=f_idx, tip_id=tip.tip_id
                        )
                    )
            else:
                print("⚠️ Tracking lost in this frame")
                # Pass through raw tips
                for tip in raw_tips:
                    mapped_tips.append(tip)
        else:
            # Fallback if no tracker (should not happen if setup is correct)
            for tip in raw_tips:
                mapped_tips.append(tip)

        result: Dict[str, Any] = {
            "fingertips": [
                {"x": t.x, "y": t.y, "string": t.string, "fret": t.fret, "tip_id": t.tip_id}
                for t in mapped_tips
            ],
            "homography": current_H.tolist() if current_H is not None else None,
            "image_size": {"width": full_bgr.shape[1], "height": full_bgr.shape[0]}
        }

        # 3) Scoring
        if expected_positions is not None:
            correct: List[Dict[str, int]] = []
            missing: List[Dict[str, int]] = []
            extra: List[Dict[str, int]] = []

            used_tip_indices = set()

            for exp in expected_positions:
                best_i = None
                for i, tip in enumerate(mapped_tips):
                    if i in used_tip_indices: continue
                    if tip.string == exp.string and tip.fret == exp.fret:
                        best_i = i
                        break

                if best_i is not None:
                    used_tip_indices.add(best_i)
                    correct.append({"string": exp.string, "fret": exp.fret})
                else:
                    missing.append({"string": exp.string, "fret": exp.fret})

            for i, tip in enumerate(mapped_tips):
                if i not in used_tip_indices and tip.string is not None and tip.fret is not None:
                    extra.append({"string": tip.string, "fret": tip.fret})

            score = 0.0
            if expected_positions:
                score = len(correct) / float(len(expected_positions))

            result.update(
                {
                    "expected": [exp.__dict__ for exp in expected_positions],
                    "correct": correct,
                    "missing": missing,
                    "extra": extra,
                    "score": score,
                }
            )

        return result


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python mediapipe_finger_detection.py path/to/image.jpg")
        sys.exit(0)

    img_path = sys.argv[1]
    img = cv2.imread(img_path)
    analyzer = FingerAnalyzer()
    
    # For single image test, we might need to rotate it first if the tracker expects rotated images?
    # Our generate_reference_grid SAVED a rotated image.
    # So we should rotate the input image too to match orientation roughly for SIFT.
    from rotate_crop import rotate_neck_picture
    img_obj = Image(img=img)
    neck_rot = rotate_neck_picture(img_obj)
    
    out = analyzer.analyze(neck_rot.image, expected_positions=None)
    print("Detected fingertips:")
    for t in out["fingertips"]:
        print(t)
