from ultralytics import YOLO
import os

def train():
    # 1. Load a model
    # 使用 yolov8n-pose.pt (nano 版本，速度最快)
    # 第一次运行会自动下载权重
    model = YOLO('yolov8n-pose.pt')  

    # 2. Train the model
    # mps 是 Mac M1/M2 的 GPU 加速
    device = 'mps' if os.uname().sysname == 'Darwin' else 'cpu'
    
    print(f"Starting training on {device}...")
    
    results = model.train(
        data='fretboard.yaml',
        epochs=100,             # 训练 100 轮 (因为数据少，可以多练会儿，或者先设 50 看看)
        imgsz=640,             # 图像大小
        batch=16,              # 批次大小 (如果 M2 只有 8G 内存，报错的话改成 8 或 4)
        device=device,
        project='runs/pose',   # 结果保存路径
        name='fretboard_v1',   # 实验名称
        plots=True,            # 画出训练曲线
        save=True              # 保存模型
    )

    print("Training finished!")
    print(f"Best model saved at: {results.save_dir}/weights/best.pt")

if __name__ == '__main__':
    # 确保我们在 Backend 目录下运行，否则路径可能对不上
    if not os.path.exists('fretboard.yaml'):
        print("Error: fretboard.yaml not found. Please run this script from the Backend directory.")
    else:
        train()

