"""
Test script for MediaPipe-based finger detection on pictures2 images using HOMOGRAPHY TRACKING.

Run inside venv:
    cd /Users/zhangboxiang/Desktop/CVMusic/Backend
    source venv/bin/activate
    python test_pictures2_fingers.py
"""

import os
import json
from typing import Dict, List, Tuple

import cv2
import numpy as np

from mediapipe_finger_detection import FingerAnalyzer, ExpectedPosition
from image import Image
from rotate_crop import rotate_neck_picture, resize_image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PICTURES2_DIR = os.path.join(BASE_DIR, "pictures2")
OUTPUT_DIR = os.path.join(BASE_DIR, "test_results", "mediapipe")
GRID_JSON_PATH = os.path.join(BASE_DIR, "reference_grid.json")

# Expected open-chord fingerings
CHORD_LIBRARY: Dict[str, List[ExpectedPosition]] = {
    "C": [
        ExpectedPosition(string=5, fret=3),
        ExpectedPosition(string=4, fret=2),
        ExpectedPosition(string=2, fret=1),
    ],
    "Am": [
        ExpectedPosition(string=4, fret=2),
        ExpectedPosition(string=3, fret=2),
        ExpectedPosition(string=2, fret=1),
    ],
    "D": [
        ExpectedPosition(string=3, fret=2),
        ExpectedPosition(string=1, fret=2),
        ExpectedPosition(string=2, fret=3),
    ],
}

def chord_name_from_filename(filename: str) -> str:
    base = os.path.splitext(filename)[0].lower()
    if "chordam" in base: return "Am"
    if "chordc" in base: return "C"
    if "chordd" in base: return "D"
    return ""

def load_reference_grid():
    if not os.path.exists(GRID_JSON_PATH):
        return None
    with open(GRID_JSON_PATH, 'r') as f:
        return json.load(f)

def draw_results(img, results, outfile: str) -> None:
    vis = img.copy()
    
    # If Homography is present, project and draw the Reference Grid!
    H = results.get("homography")
    grid_data = load_reference_grid()
    
    if H is not None and grid_data:
        H = np.array(H)
        
        # Helper to project a point (x, y) using H
        def project_point(x, y):
            pt = np.array([[[float(x), float(y)]]], dtype=np.float32)
            dst = cv2.perspectiveTransform(pt, H)
            return tuple(map(int, dst[0][0]))

        # 1. Draw Strings
        strings = grid_data.get("strings", {})
        for name, pts in strings.items():
            # pts is [[x1, y1], [x2, y2]]
            p1 = project_point(pts[0][0], pts[0][1])
            p2 = project_point(pts[1][0], pts[1][1])
            
            cv2.line(vis, p1, p2, (0, 255, 255), 2) # Yellow strings
            # Label string name near p1
            cv2.putText(vis, name, p1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 200), 1)

        # 2. Draw Fret Lines
        fret_lines = grid_data.get("fret_lines", [])
        for i, pts in enumerate(fret_lines):
            p1 = project_point(pts[0][0], pts[0][1])
            p2 = project_point(pts[1][0], pts[1][1])
            
            cv2.line(vis, p1, p2, (255, 0, 255), 2) # Magenta frets
            # Label fret number near top
            cv2.putText(vis, str(i), (p1[0], p1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 255), 1)
            
        cv2.putText(vis, "TRACKING LOCKED", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    else:
        cv2.putText(vis, "TRACKING LOST", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    fingertips = results.get("fingertips", [])
    for tip in fingertips:
        x = tip["x"]
        y = tip["y"]
        string = tip.get("string")
        fret = tip.get("fret")

        # Draw fingertip point
        color = (0, 255, 0) if (string is not None and fret is not None) else (0, 0, 255)
        cv2.circle(vis, (x, y), 8, color, -1)

        # Put (string,fret) label
        label = ""
        if string is not None: label += f"S{string} "
        if fret is not None: label += f"F{fret}"
        
        if label:
            cv2.putText(vis, label, (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    cv2.imwrite(outfile, vis)

def main() -> None:
    print("=" * 60)
    print("🎸 Testing Homography-based Finger Detection")
    print("=" * 60)

    if not os.path.isdir(PICTURES2_DIR):
        print(f"❌ Directory not found: {PICTURES2_DIR}")
        return

    analyzer = FingerAnalyzer()

    filenames = sorted(
        f for f in os.listdir(PICTURES2_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))
    )

    for fname in filenames:
        path = os.path.join(PICTURES2_DIR, fname)
        print("\n" + "-" * 60)
        print(f"📷 Image: {fname}")

        full_img = cv2.imread(path)
        if full_img is None: continue

        # 1) Resize & Rotate to match Reference Orientation
        # (The reference was generated from a Rotated image, so we must rotate input too)
        img_resized = resize_image(full_img)
        img_obj = Image(img=img_resized)
        neck_rot = rotate_neck_picture(img_obj)
        rotated_frame = neck_rot.image.copy()

        chord_name = chord_name_from_filename(fname)
        expected = CHORD_LIBRARY.get(chord_name, None)
        
        if expected:
            print(f"🎼 Expected chord: {chord_name}")
            for pos in expected:
                print(f"   - String {pos.string}, Fret {pos.fret}")

        try:
            results = analyzer.analyze(
                full_bgr=rotated_frame,
                expected_positions=expected,
            )
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            continue

        fingertips = results.get("fingertips", [])
        print(f"👉 Detected fingertips: {len(fingertips)}")
        for tip in fingertips:
            print(f"   - x={tip['x']:4d}, y={tip['y']:4d} -> S{tip.get('string')} F{tip.get('fret')}")

        if expected is not None:
            print("✅ Correct:", results.get("correct", []))
            print("❌ Missing:", results.get("missing", []))
            print("📊 Score:", results.get("score"))

        # Save visualization
        out_path = os.path.join(OUTPUT_DIR, f"tracked_{fname}")
        draw_results(rotated_frame, results, out_path)
        print(f"💾 Visualization saved to: {out_path}")

    print("\n" + "=" * 60)
    print("✅ Test finished")
    print("=" * 60)

if __name__ == "__main__":
    main()
