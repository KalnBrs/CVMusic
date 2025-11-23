import cv2
from ultralytics import YOLO
import numpy as np
from Vector2 import Vector2
import os

model = None


def load_model():
    global model

    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "..", "runs", "pose", "fretboard_v2_small_aug2_65", "weights", "best.pt")

    print(f"Loading model from: {model_path}")

    try:
        model = YOLO(model_path)
        return model

    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please check if the path is correct and the file exists.")
        model = None
        return None


def get_fretboard_corners(img):
    global model

    # Load model if needed
    if model is None:
        model = load_model()
        if model is None:
            print("❌ Model failed to load.")
            return None

    # Run inference
    results = model(img, conf=0.3, verbose=False)

    
    r = results[0]

    print("\n--- DEBUG ---")
    print("Results", results)
    print("Detections:", len(r.boxes))
    print("Keypoints object:", r.keypoints)

    # No detections at all
    if r.keypoints is None:
        print("❌ No keypoints attribute in results.")
        return None

    if r.keypoints.data is None:
        print("❌ Keypoints.data is None.")
        return None

    kpts = r.keypoints.data.cpu().numpy()

    print("Keypoints array shape:", kpts.shape)
    print("Raw keypoints:\n", kpts)

    # No detected instances
    if len(kpts) == 0:
        print("❌ Model detected 0 objects.")
        return None

    kp_set = kpts[0]   # first detection

    print("First detection keypoints:", kp_set)

    if len(kp_set) != 4:
        print("❌ Expected 4 keypoints, got", len(kp_set))
        return None

    points = []
    for i, (x, y, conf) in enumerate(kp_set):
        print(f"Keypoint {i}: x={x}, y={y}, conf={conf}")
        if conf > 0.3:
            points.append(Vector2(x, y))

    if len(points) != 4:
        print("❌ Not all 4 keypoints had conf > 0.5")
        return None

    print("✅ Returning 4 corners:", points)
    return tuple(points)

