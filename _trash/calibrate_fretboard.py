"""
Interactive tool to calibrate the fretboard grid on a reference image.

Usage (inside venv):

    cd /Users/zhangboxiang/Desktop/CVMusic/Backend
    source venv/bin/activate
    python calibrate_fretboard.py pictures2/chordC.jpg

Steps on the image window:
  1) First, click TWO points along String 1 (high E), then String 2, ..., up to String 6.
     - Each string: 2 left-clicks to define a line.
  2) Then, click TWO points along Fret 1, Fret 2, ..., up to Fret 5 (or however many you want).
  3) When done, the calibration will be saved to:
         Backend/calibration/fretboard_calibration.json

This JSON will later be used by FingerAnalyzer to map fingertip pixels -> (string, fret)
without relying on Hough-based grid detection.
"""

import json
import os
import sys
from typing import List, Tuple

import cv2


N_STRINGS = 6
N_FRETS = 5  # number of frets you care about near the nut


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python calibrate_fretboard.py path/to/reference_image.jpg")
        sys.exit(0)

    img_path = sys.argv[1]
    if not os.path.isfile(img_path):
        print(f"❌ Image not found: {img_path}")
        sys.exit(1)

    img = cv2.imread(img_path)
    if img is None:
        print(f"❌ Cannot read image: {img_path}")
        sys.exit(1)

    h, w = img.shape[:2]
    display = img.copy()

    strings: List[dict] = []
    frets: List[dict] = []

    mode = "string"  # or "fret"
    current_string = 1
    current_fret = 1
    temp_points: List[Tuple[int, int]] = []

    window_name = "Calibrate Fretboard"

    print("============================================================")
    print("🎯 Fretboard Calibration")
    print("============================================================")
    print(f"Image: {img_path} (width={w}, height={h})")
    print()
    print("Instructions:")
    print("  1) First click TWO points along each string, from String 1 (high E) to String 6 (low E).")
    print("  2) Then click TWO points along each fret line (from Fret 1 upwards).")
    print("  3) Press 'q' to cancel at any time.")
    print()

    def mouse_cb(event, x, y, flags, param):
        nonlocal mode, current_string, current_fret, temp_points, display

        if event == cv2.EVENT_LBUTTONDOWN:
            temp_points.append((x, y))
            cv2.circle(display, (x, y), 4, (0, 0, 255), -1)

            if len(temp_points) == 2:
                p1, p2 = temp_points
                color = (0, 255, 255) if mode == "string" else (255, 0, 255)
                cv2.line(display, p1, p2, color, 2)

                if mode == "string":
                    strings.append(
                        {
                            "index": current_string,
                            "p1": [int(p1[0]), int(p1[1])],
                            "p2": [int(p2[0]), int(p2[1])],
                        }
                    )
                    print(f"✅ Recorded String {current_string}: {p1} -> {p2}")
                    current_string += 1
                else:
                    frets.append(
                        {
                            "index": current_fret,
                            "p1": [int(p1[0]), int(p1[1])],
                            "p2": [int(p2[0]), int(p2[1])],
                        }
                    )
                    print(f"✅ Recorded Fret {current_fret}: {p1} -> {p2}")
                    current_fret += 1

                temp_points = []

    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, mouse_cb)

    while True:
        # Draw instruction text on a copy to avoid overwriting base drawing
        overlay = display.copy()
        if mode == "string":
            text = f"Click 2 points for String {current_string}/{N_STRINGS} (high E is String 1)."
        else:
            text = f"Click 2 points for Fret {current_fret}/{N_FRETS}."

        cv2.putText(
            overlay,
            text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )

        cv2.imshow(window_name, overlay)
        key = cv2.waitKey(20) & 0xFF

        if key == ord("q"):
            print("❌ Calibration cancelled by user.")
            cv2.destroyAllWindows()
            sys.exit(0)

        # Switch from strings to frets
        if mode == "string" and current_string > N_STRINGS:
            print("🎸 Finished string lines, now calibrate frets.")
            mode = "fret"

        # Finish once all frets are done
        if mode == "fret" and current_fret > N_FRETS:
            print("🎉 Finished fret lines.")
            break

    cv2.destroyAllWindows()

    if len(strings) < N_STRINGS:
        print(f"⚠️ Only {len(strings)} strings recorded, expected {N_STRINGS}.")
    if len(frets) < 1:
        print("⚠️ No frets recorded.")

    calib = {
        "image_width": w,
        "image_height": h,
        "strings": strings,
        "frets": frets,
    }

    calib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "calibration")
    os.makedirs(calib_dir, exist_ok=True)
    out_path = os.path.join(calib_dir, "fretboard_calibration.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(calib, f, indent=2)

    print()
    print("============================================================")
    print(f"✅ Calibration saved to: {out_path}")
    print("============================================================")


if __name__ == "__main__":
    main()


