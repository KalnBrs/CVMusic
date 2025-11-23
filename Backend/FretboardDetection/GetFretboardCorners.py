import cv2
from ultralytics import YOLO
import numpy as np
from Vector2 import Vector2

def get_fretboard_corners(img):
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, "..", "runs", "pose", "fretboard_v19", "weights", "best.pt")
    
    print(f"Loading model from: {model_path}")
    try:
        model = YOLO(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please check if the path is correct and the file exists.")
        return

    # Run inference
        # conf=0.5: Only show detections with >50% confidence
        # Force CPU because RTX 5060 is too new for current PyTorch CUDA binaries
        results = model(img, conf=0.5, verbose=False, device='cpu')

        # Visualize results
        # plot() returns the image with boxes/keypoints drawn
        annotated_frame = results[0].plot()

        # Optional: Custom drawing if you want to connect keypoints specifically
        # The keypoints are in results[0].keypoints
        # shape: (num_dets, 4, 3) -> (x, y, conf)
        
        if results[0].keypoints is not None and results[0].keypoints.data is not None:
            kpts = results[0].keypoints.data.cpu().numpy()
            if len(kpts) > 0:
                # Assuming we want the corners of the first detected fretboard
                kp_set = kpts[0]
                # kp_set is (4, 3) -> (x, y, conf)
                # 0: TL, 1: TR, 2: BR, 3: BL
                if len(kp_set) == 4:
                    points_vector2 = []
                    for i in range(4):
                        x, y, conf = kp_set[i]
                        if conf > 0.5:  # Only include points with sufficient confidence
                            points_vector2.append(Vector2(x, y))
                    if len(points_vector2) == 4:
                        return tuple(points_vector2)
        return None  # Return None if no valid fretboard corners are found
