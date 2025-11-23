import json
import os
import cv2

def create_manual_grid():
    # Load the reference image to get dimensions
    ref_img_path = "Backend/reference_neck.jpg"
    if not os.path.exists(ref_img_path):
        ref_img_path = "reference_neck.jpg" # Try local
        
    img = cv2.imread(ref_img_path)
    if img is None:
        print(f"❌ Cannot load {ref_img_path}")
        return
        
    h, w = img.shape[:2]
    print(f"📏 Reference Image Size: {w}x{h}")
    
    # --- 手动校准参数 ---
    
    # 1. 琴枕 (Nut)
    # D和弦时F2, F3很准，说明这个参数目前还可以。
    NUT_X = int(w * 0.81) 
    
    # 2. 弦长 (Scale Length)
    SCALE_LENGTH = int(w * 0.95) 
    
    # 3. 弦的高度 (Y轴) - 修正版
    # 之前的弦严重偏下 (识别成 S4/S5/S6，实际是 S1/S2/S3)。
    # 所以我们需要把 Y 值变小（向上移）。
    # 之前 BOARD_CENTER = h // 2 (1548)。
    # 我们把它向上提 200 像素试试。
    
    BOARD_CENTER = (h // 2) - 180 
    
    # 之前的宽度是 h * 0.08 (247px半宽)，看起来有点窄，因为 D 和弦都挤在一起了。
    # 稍微加宽一点点。
    BOARD_HALF_WIDTH = int(h * 0.10) 
    
    STRING_1_Y = BOARD_CENTER - BOARD_HALF_WIDTH  
    STRING_6_Y = BOARD_CENTER + BOARD_HALF_WIDTH  
    
    # -------------------------------------------------------
    
    grid_data = {
        "strings": {},
        "fret_lines": []
    }
    
    # 生成 6 根弦
    for i in range(1, 7): # 1..6 (1=High E, 6=Low E)
        # 线性插值计算每根弦的 Y
        t = (i - 1) / 5.0
        y = STRING_1_Y + t * (STRING_6_Y - STRING_1_Y)
        
        # 弦从左到右贯穿
        grid_data["strings"][str(i)] = [
            [0, int(y)], 
            [w, int(y)]
        ]
        
    # 生成品格 (0品 到 20品)
    fret_lines = []
    for n in range(0, 21): # 0..20
        dist = SCALE_LENGTH * (1 - (2 ** (-n / 12.0)))
        x = NUT_X - dist
        
        if x < 0: break 
        
        fret_lines.append([
            [int(x), 0],
            [int(x), h]
        ])
        
    grid_data["fret_lines"] = fret_lines
    
    out_path = "Backend/reference_grid.json"
    if not os.path.exists("Backend"):
        out_path = "reference_grid.json"
        
    with open(out_path, "w") as f:
        json.dump(grid_data, f, indent=2)
        
    print(f"✅ 已重置 {out_path} (弦向上修正版)")
    print(f"Nut: {NUT_X}, Strings: {STRING_1_Y}-{STRING_6_Y}")

if __name__ == "__main__":
    create_manual_grid()
