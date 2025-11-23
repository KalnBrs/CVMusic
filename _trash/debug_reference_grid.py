import cv2
import json
import os
import numpy as np

def debug_reference_grid():
    ref_img_path = "Backend/reference_neck.jpg"
    if not os.path.exists(ref_img_path):
        ref_img_path = "reference_neck.jpg"
        
    grid_path = "Backend/reference_grid.json"
    if not os.path.exists(grid_path):
        grid_path = "reference_grid.json"
        
    img = cv2.imread(ref_img_path)
    if img is None:
        print("❌ No reference image found.")
        return
        
    with open(grid_path, 'r') as f:
        grid_data = json.load(f)
        
    vis = img.copy()
    h, w = img.shape[:2]
    
    # Draw Strings
    for name, pts in grid_data["strings"].items():
        p1 = tuple(map(int, pts[0]))
        p2 = tuple(map(int, pts[1]))
        cv2.line(vis, p1, p2, (0, 255, 255), 3)
        cv2.putText(vis, f"S{name}", (p1[0]+20, p1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
        
    # Draw Frets
    for i, pts in enumerate(grid_data["fret_lines"]):
        p1 = tuple(map(int, pts[0]))
        p2 = tuple(map(int, pts[1]))
        cv2.line(vis, p1, p2, (255, 0, 255), 3)
        if i % 3 == 0: # Label every 3rd fret to avoid clutter
            cv2.putText(vis, str(i), (p1[0], 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 255), 3)
            
    out_path = "Backend/reference_grid_CHECK.jpg"
    if not os.path.exists("Backend"):
        out_path = "reference_grid_CHECK.jpg"
        
    cv2.imwrite(out_path, vis)
    print(f"🖼 保存了基准网格检查图: {out_path}")
    print("请打开这张图，检查网格是否对齐了琴颈。")

if __name__ == "__main__":
    debug_reference_grid()

