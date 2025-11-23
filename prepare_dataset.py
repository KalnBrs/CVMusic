import cv2
import os
import shutil

def prepare_yolo_dataset(video_path="guitar_train.mp4", output_base="datasets", interval=30):
    """
    从视频中自动切图，准备 YOLO 训练数据
    video_path: 视频文件路径
    output_base: 输出目录
    interval: 每隔多少帧保存一张 (防止图片过于相似)
    """
    
    # 1. 检查视频
    if not os.path.exists(video_path):
        print(f"❌ 找不到视频文件: {video_path}")
        print("请录制一段拿着吉他移动的视频，重命名为 guitar_train.mp4 放在 Backend 目录下。")
        return

    # 2. 准备目录结构
    # YOLO 目录结构:
    # datasets/
    #   images/
    #     train/
    #     val/
    #   labels/  (标注时会自动生成)
    #     train/
    #     val/
    
    images_train_dir = os.path.join(output_base, "images", "train")
    images_val_dir = os.path.join(output_base, "images", "val")
    
    # 清理旧数据 (可选，这里选择如果存在就直接覆盖/添加)
    if os.path.exists(output_base):
        print(f"⚠️ 目录 {output_base} 已存在，新图片将追加进去。")
    
    os.makedirs(images_train_dir, exist_ok=True)
    os.makedirs(images_val_dir, exist_ok=True)
    
    # 3. 开始切图
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_count = 0
    
    print("🎥 开始处理视频...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        
        # 每隔 interval 帧保存一次
        if frame_count % interval == 0:
            # 模糊检测 (Laplacian 方差)
            # 如果数值太低 (<100)，说明图片很模糊，不适合做训练集
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            if blur_score < 60: # 阈值可调
                print(f"   ⏩ 跳过模糊帧 {frame_count} (Score: {blur_score:.1f})")
                continue
            
            # 80% 放入 train, 20% 放入 val
            if saved_count % 5 == 0: # 每5张里的一张给验证集
                save_path = os.path.join(images_val_dir, f"frame_{frame_count:06d}.jpg")
            else:
                save_path = os.path.join(images_train_dir, f"frame_{frame_count:06d}.jpg")
                
            cv2.imwrite(save_path, frame)
            saved_count += 1
            print(f"   ✅ 保存: {save_path} (Blur: {blur_score:.1f})")
            
    cap.release()
    print(f"\n🎉 处理完成！共保存 {saved_count} 张图片。")
    print(f"📂 图片位置: {output_base}/images")
    print("👉 下一步: 使用 LabelImg 或 Roboflow 进行标注。")

if __name__ == "__main__":
    # 确保在 Backend 目录下运行
    if os.path.basename(os.getcwd()) != "Backend":
        print("⚠️ 请 cd 到 Backend 目录下运行此脚本")
    else:
        prepare_yolo_dataset()
