import cv2
import numpy as np
import time
from collections import deque
from mediapipe_finger_detection import FingerAnalyzer, ExpectedPosition, DetectedFingertip

class HomographySmoother:
    """
    Simple moving average smoother for Homography matrix.
    Reduces jitter/shaking of the projected grid.
    """
    def __init__(self, history_size=5):
        self.history = deque(maxlen=history_size)
    
    def update(self, H):
        if H is None:
            return None
        
        self.history.append(H)
        
        # Calculate average matrix
        H_avg = np.mean(np.array(self.history), axis=0)
        return H_avg
    
    def reset(self):
        self.history.clear()

def main():
    print("🎸 正在启动 Am 和弦实时挑战 (防抖增强版)...")
    
    try:
        analyzer = FingerAnalyzer()
        if not analyzer.tracker:
            print("❌ 错误：未加载到标定数据。请先运行 setup_grid_interactive.py")
            return
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return

    smoother = HomographySmoother(history_size=5) # 平滑最近5帧，数值越大越稳但延迟越高

    # Target: Am
    target_chord_name = "Am"
    target_positions = [
        ExpectedPosition(string=2, fret=1),
        ExpectedPosition(string=3, fret=2),
        ExpectedPosition(string=4, fret=2)
    ]
    
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return

    print("✅ 摄像头已启动！请按 'q' 退出。")

    fps_time = time.time()
    frame_count = 0
    fps = 0
    
    # Tracking state
    is_tracking = False
    lost_frames = 0
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # Analyze
        results = analyzer.analyze(frame, expected_positions=target_positions)
        
        # --- Visualization ---
        vis = frame.copy()
        
        # Smooth Tracking
        raw_H = results.get("homography")
        
        if raw_H is not None:
            raw_H = np.array(raw_H)
            is_tracking = True
            lost_frames = 0
            H = smoother.update(raw_H)
        else:
            lost_frames += 1
            if lost_frames > 10: # If lost for 10 frames, reset smoother
                is_tracking = False
                smoother.reset()
                H = None
            else:
                # Use last known good matrix for a few frames (coast)
                if len(smoother.history) > 0:
                    H = np.mean(np.array(smoother.history), axis=0)
                else:
                    H = None

        # Draw Grid
        if is_tracking and H is not None:
            if analyzer.grid_system:
                def proj(x, y):
                    pt = np.array([[[float(x), float(y)]]], dtype=np.float32)
                    dst = cv2.perspectiveTransform(pt, H)
                    return tuple(map(int, dst[0][0]))

                # Draw Strings
                for name, pts in analyzer.grid_system.strings.items():
                    p1 = proj(pts[0][0], pts[0][1])
                    p2 = proj(pts[1][0], pts[1][1])
                    cv2.line(vis, p1, p2, (0, 255, 255), 2)
                
                # Draw Frets
                for i, pts in enumerate(analyzer.grid_system.fret_lines):
                    p1 = proj(pts[0][0], pts[0][1])
                    p2 = proj(pts[1][0], pts[1][1])
                    cv2.line(vis, p1, p2, (255, 0, 255), 2)
                    if i % 3 == 0:
                        cv2.putText(vis, str(i), (p1[0], p1[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,255), 1)

            status_text = "TRACKING STABLE"
            status_color = (0, 255, 0)
        else:
            status_text = "SEARCHING..."
            status_color = (0, 0, 255)
            
        cv2.putText(vis, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)

        # Draw Fingertips
        fingertips = results.get("fingertips", [])
        for tip in fingertips:
            x, y = tip["x"], tip["y"]
            # Recalculate mapping using SMOOTHED H
            s, f = None, None
            if is_tracking and H is not None and analyzer.tracker:
                # Remap using smoothed matrix for consistency
                ref_pt = analyzer.tracker.map_point_to_reference(x, y, H)
                if ref_pt:
                    rx, ry = ref_pt
                    s = analyzer.grid_system.get_string_index(rx, ry)
                    f = analyzer.grid_system.get_fret_index(rx, ry)
            
            # Color logic
            color = (0, 255, 255)
            label = ""
            if s is not None and f is not None:
                label = f"S{s} F{f}"
                # Check if this specific finger is part of the required chord
                is_required = False
                for req in target_positions:
                    if req.string == s and req.fret == f:
                        is_required = True
                        break
                color = (0, 255, 0) if is_required else (0, 165, 255) # Green for correct note, Orange for wrong note
            else:
                color = (0, 0, 255)
                
            cv2.circle(vis, (x, y), 8, color, -1)
            if label:
                cv2.putText(vis, label, (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Score Logic (Re-evaluate based on Smoothed Mapping)
        # We need to manually check correctness because 'results' used raw H
        # But for display demo, 'results' score is okay-ish, but visual feedback matters more.
        
        score = results.get("score", 0.0) # Using raw score for now
        
        cv2.putText(vis, f"Target: {target_chord_name}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        if score >= 0.9: # Allow some tolerance
            cv2.putText(vis, "MATCHED! EXCELLENT!", (20, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

        # FPS
        frame_count += 1
        if time.time() - fps_time > 1.0:
            fps = frame_count / (time.time() - fps_time)
            frame_count = 0
            fps_time = time.time()
        cv2.putText(vis, f"FPS: {fps:.1f}", (vis.shape[1]-150, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

        cv2.imshow('Guitar Hero Live Demo', vis)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
