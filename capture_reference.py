import cv2
import os

def capture_reference_image():
    print("📷 正在打开摄像头...")
    cap = cv2.VideoCapture(0)
    
    # 尝试设置高分辨率 (如果摄像头支持)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    if not cap.isOpened():
        print("❌ 无法打开摄像头！")
        return

    print("\n=== 操作指南 ===")
    print("1. 请将吉他【琴颈】完整地放入画面中。")
    print("2. 尽量正对摄像头，光线充足。")
    print("3. 按【空格键】拍照并保存。")
    print("4. 按【Q】键退出。")
    print("================\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取画面")
            break
            
        # 画一个辅助框，提示用户把琴颈放中间
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (int(w*0.1), int(h*0.3)), (int(w*0.9), int(h*0.7)), (0, 255, 0), 2)
        cv2.putText(frame, "Put Fretboard Here", (int(w*0.1), int(h*0.25)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow('Capture Reference', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord(' '): # Space bar
            save_path = "reference_neck.jpg"
            # 如果在 Backend 目录下运行，确保路径正确
            if os.path.basename(os.getcwd()) == "Backend":
                save_path = "reference_neck.jpg"
            elif os.path.exists("Backend"):
                save_path = "Backend/reference_neck.jpg"
                
            cv2.imwrite(save_path, frame)
            print(f"✅ 已保存基准图: {save_path}")
            print("现在请运行: python setup_grid_interactive.py 进行标定")
            break
            
        if key == ord('q'):
            print("已取消")
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_reference_image()

