import cv2
import json
import os
import numpy as np

# Global variables for mouse callback
points = []
img_display = None

def click_event(event, x, y, flags, param):
    global points, img_display
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        # Visual feedback
        cv2.circle(img_display, (x, y), 10, (0, 0, 255), -1)
        cv2.putText(img_display, str(len(points)), (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Calibration", img_display)

def setup_interactive():
    global img_display, points
    
    ref_path = "Backend/reference_neck.jpg"
    if not os.path.exists(ref_path):
        ref_path = "reference_neck.jpg"
        
    if not os.path.exists(ref_path):
        print(f"❌ 找不到基准图: {ref_path}")
        print("请先运行 generate_reference_grid.py 生成基准图 (哪怕 grid 不准也没关系，我们需要图)")
        return

    img = cv2.imread(ref_path)
    img_display = img.copy()
    h, w = img.shape[:2]
    
    print("========================================================")
    print("🎸 交互式吉他指板标定工具")
    print("========================================================")
    print("请在弹出的窗口中，依次点击指板的 4 个角落：")
    print("1. 【琴枕 (0品) - 上方】 (第1弦, 高音弦)")
    print("2. 【琴枕 (0品) - 下方】 (第6弦, 低音弦)")
    print("3. 【琴身端 (高品) - 上方】 (第1弦, 高音弦)")
    print("4. 【琴身端 (高品) - 下方】 (第6弦, 低音弦)")
    print("--------------------------------------------------------")
    print("点击满 4 个点后，按任意键完成。")
    print("如果点错了，请重新运行脚本。")
    
    cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
    # Resize window if image is huge (4K)
    if w > 1800:
        cv2.resizeWindow("Calibration", 1600, int(1600 * h / w))
        
    cv2.setMouseCallback("Calibration", click_event)
    cv2.imshow("Calibration", img_display)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if len(points) != 4:
        print(f"❌ 你点击了 {len(points)} 个点，需要正好 4 个点。请重试。")
        return
        
    print(f"✅ 捕获坐标: {points}")
    
    # Sort points to ensure logical mapping regardless of click order, 
    # BUT we trust the user followed instructions 1->2->3->4 better.
    # Let's assume 1:TL, 2:BL, 3:TR, 4:BR (Left=Nut, Right=Body)
    # OR 1:TR, 2:BR, 3:TL, 4:BL (Right=Nut, Left=Body)
    # Based on tracked_chordD.jpg, Nut is on the RIGHT.
    # So "Nut" points should have larger X than "Body" points.
    
    p1, p2, p3, p4 = points
    
    # Let's sort by X to determine orientation
    avg_x_12 = (p1[0] + p2[0]) / 2
    avg_x_34 = (p3[0] + p4[0]) / 2
    
    nut_points = []
    body_points = []
    
    if avg_x_12 > avg_x_34:
        # 1,2 are Nut (Right), 3,4 are Body (Left)
        print("检测到琴头在【右侧】")
        nut_points = [p1, p2]
        body_points = [p3, p4]
    else:
        # 1,2 are Nut (Left), 3,4 are Body (Right)
        print("检测到琴头在【左侧】")
        nut_points = [p1, p2] # Actually these are Nut
        body_points = [p3, p4]
        
    # Sort by Y to separate String 1 (Top) and String 6 (Bottom)
    # Smaller Y is Top
    nut_points.sort(key=lambda p: p[1])
    body_points.sort(key=lambda p: p[1])
    
    # Now we have explicit corners
    nut_top = nut_points[0]    # String 1 Nut
    nut_bot = nut_points[1]    # String 6 Nut
    body_top = body_points[0]  # String 1 Body
    body_bot = body_points[1]  # String 6 Body
    
    # Generate Grid
    grid_data = {
        "strings": {},
        "fret_lines": []
    }
    
    # 1. Interpolate Strings
    # We have 6 strings.
    for i in range(1, 7): # 1..6
        t = (i - 1) / 5.0
        # Interpolate start point (at Nut)
        sx = nut_top[0] + t * (nut_bot[0] - nut_top[0])
        sy = nut_top[1] + t * (nut_bot[1] - nut_top[1])
        
        # Interpolate end point (at Body)
        ex = body_top[0] + t * (body_bot[0] - body_top[0])
        ey = body_top[1] + t * (body_bot[1] - body_top[1])
        
        # Extend the lines slightly to cover full image width if needed?
        # Better to keep them strictly within the clicked region for accuracy.
        grid_data["strings"][str(i)] = [
            [int(sx), int(sy)],
            [int(ex), int(ey)]
        ]
        
    # 2. Generate Frets
    # We need Scale Length.
    # Distance from Nut to 12th Fret is Scale/2.
    # Did the user click the 12th fret as the "Body" point? 
    # Usually users click the end of the image.
    # Let's assume the "Body Points" are roughly around Fret 12-15.
    # Let's dynamically estimate Scale based on visual length assuming the clicked region is ~12 frets.
    # A standard neck join is at 14th fret. Let's assume the user clicked near the 14th fret area.
    
    # Calculate pixel length of the board
    len_top = np.linalg.norm(np.array(nut_top) - np.array(body_top))
    len_bot = np.linalg.norm(np.array(nut_bot) - np.array(body_bot))
    avg_len = (len_top + len_bot) / 2
    
    # Formula: dist_n = Scale * (1 - 2^(-n/12))
    # If avg_len corresponds to fret N (e.g. 14), then:
    # avg_len = Scale * (1 - 2^(-14/12))
    # Scale = avg_len / (1 - 2^(-14/12))
    ASSUMED_LAST_FRET = 14
    factor = 1 - (2 ** (-ASSUMED_LAST_FRET / 12.0))
    scale_px = avg_len / factor
    
    print(f"推算 Scale: {scale_px:.1f} px (假设你点的是第 {ASSUMED_LAST_FRET} 品)")
    
    # Generate 20 fret lines
    for n in range(0, 21):
        ratio = (1 - (2 ** (-n / 12.0)))
        dist = scale_px * ratio
        
        # We need to interpolate along the "fretboard axis"
        # Vector from Nut to Body
        vec_top = np.array(body_top) - np.array(nut_top)
        vec_bot = np.array(body_bot) - np.array(nut_bot)
        
        # Normalize vectors is not needed, we use ratio of the TOTAL clicked length
        # But wait, the total clicked length is only up to ASSUMED_LAST_FRET
        # So dist is pixels from Nut.
        # We need to map "pixels from Nut" to "t (0..1) along the clicked quad"
        
        # t = dist / avg_len  (Roughly)
        t = dist / avg_len
        
        # Clamp? No, we want to draw even if it goes beyond clicked area
        
        p_top = np.array(nut_top) + vec_top * t
        p_bot = np.array(nut_bot) + vec_bot * t
        
        grid_data["fret_lines"].append([
            p_top.tolist(),
            p_bot.tolist()
        ])
        
    # Save
    out_path = "Backend/reference_grid.json"
    if not os.path.exists("Backend"):
        out_path = "reference_grid.json"
        
    with open(out_path, "w") as f:
        json.dump(grid_data, f, indent=2)
        
    print("✅ 校准完成！reference_grid.json 已更新。")
    print("现在请重新运行 test_pictures2_fingers.py 验证效果。")

if __name__ == "__main__":
    setup_interactive()

