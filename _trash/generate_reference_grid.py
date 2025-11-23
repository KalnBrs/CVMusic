import cv2
import json
import os
import numpy as np
from grid_detection import string_detection, detect_frets_model_based
from image import Image
from rotate_crop import rotate_neck_picture, crop_neck_with_offset

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

def generate_reference_grid(image_path: str, output_json: str):
    print(f"🔍 analyzing reference image: {image_path}")
    
    img_bgr = cv2.imread(image_path)
    if img_bgr is None:
        print("❌ Failed to load image")
        return

    # 1. Use the ROTATED version as the Reference coordinate system
    img_obj = Image(img=img_bgr)
    neck_rot = rotate_neck_picture(img_obj)
    img_rotated = neck_rot.image
    
    ref_img_path = os.path.join(os.path.dirname(output_json), "reference_neck.jpg")
    cv2.imwrite(ref_img_path, img_rotated)
    print(f"💾 Saved Rotated Reference Image to: {ref_img_path}")
    
    # 2. Crop for detection (just to find lines)
    roi_img, offset = crop_neck_with_offset(neck_rot)
    offset_x, offset_y = offset
    
    # 3. Detect Strings
    strings_obj, _ = string_detection(Image(img=roi_img))
    
    # 4. Detect Frets
    fret_xs, direction = detect_frets_model_based(Image(img=roi_img))
    
    # 5. Build JSON structure (in Reference/Rotated coordinates)
    
    grid_data = {
        "strings": {},
        "fret_lines": []
    }
    
    # Strings
    # string_detection returns lines in ROI coordinates. Add offset!
    for name, pts in strings_obj.separating_lines.items():
        # pts is [(x2, y2), (x1, y1)]
        p1 = (int(pts[1][0] + offset_x), int(pts[1][1] + offset_y))
        p2 = (int(pts[0][0] + offset_x), int(pts[0][1] + offset_y))
        
        # Map tuning name to index 1..6
        # Tuning is ["E", "A", "D", "G", "B", "E6"] -> 6, 5, 4, 3, 2, 1
        idx_map = {"E": 6, "A": 5, "D": 4, "G": 3, "B": 2, "E6": 1}
        idx = idx_map.get(name, 0)
        
        grid_data["strings"][str(idx)] = [p1, p2]
        
    # Frets
    h, w = img_rotated.shape[:2]
    
    # Sort frets 0..N
    fret_xs = sorted(fret_xs)
    if direction == -1: # Right->Left
        fret_xs.reverse()
        
    for i, x in enumerate(fret_xs):
        real_x = int(x + offset_x)
        # A vertical line from top to bottom
        grid_data["fret_lines"].append([(real_x, 0), (real_x, h)])
        
    # Save JSON
    with open(output_json, 'w') as f:
        json.dump(grid_data, f, indent=2, cls=NumpyEncoder)
        
    print(f"✅ Saved Grid JSON to: {output_json}")
    
    # 6. Draw Debug
    vis = img_rotated.copy()
    for idx, pts in grid_data["strings"].items():
        p1 = tuple(map(int, pts[0]))
        p2 = tuple(map(int, pts[1]))
        cv2.line(vis, p1, p2, (0, 255, 255), 2)
        cv2.putText(vis, f"S{idx}", p1, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)
        
    for i, pts in enumerate(grid_data["fret_lines"]):
        p1 = tuple(map(int, pts[0]))
        p2 = tuple(map(int, pts[1]))
        cv2.line(vis, p1, p2, (255, 0, 255), 2)
        cv2.putText(vis, f"{i}", (p1[0], 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255), 1)
        
    debug_path = os.path.join(os.path.dirname(output_json), "reference_grid_debug.jpg")
    cv2.imwrite(debug_path, vis)
    print(f"🖼 Saved Debug Grid to: {debug_path}")

if __name__ == "__main__":
    # Using chordD.jpg as it seems clear
    generate_reference_grid("pictures2/chordD.jpg", "reference_grid.json")
