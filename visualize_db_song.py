import cv2
import numpy as np
import json
import os
from database_manager import DatabaseManager
from fretboard_tracker import GridSystem

def visualize_song_from_db(song_id=None):
    # 1. 连接数据库
    db = DatabaseManager()
    if not db.conn: db.connect()
    
    # 如果没指定 ID，就找最新的一首
    if song_id is None:
        cur = db.conn.cursor()
        cur.execute("SELECT id, title FROM songs ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            print("❌ 数据库里没有歌！")
            return
        song_id, song_title = row
        print(f"🎵 正在可视化歌曲: {song_title} (ID: {song_id})")
    
    # 2. 获取时间轴
    timeline = db.get_song_timeline(song_id)
    if not timeline:
        print("❌ 这首歌没有时间轴数据")
        return

    # 3. 加载参考图和 Grid 系统
    ref_img_path = "reference_neck.jpg"
    grid_json_path = "reference_grid.json"
    
    if not os.path.exists(ref_img_path):
        print(f"❌ 找不到参考图: {ref_img_path}")
        return
        
    # 初始化 GridSystem (用于坐标映射)
    grid_system = GridSystem(grid_json_path)
    if not grid_system.load_grid():
        print("⚠️ 警告: 无法加载 grid json，将使用默认值 (可能不准)")
    
    ref_img = cv2.imread(ref_img_path)
    h, w = ref_img.shape[:2]

    # 创建输出目录
    output_dir = "song_visualization"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🎥 开始生成帧... (共 {len(timeline)} 个事件)")
    
    # 4. 遍历时间轴，生成演示图片
    # 为了不生成几千张图，我们只生成前 10 个有音符的事件作为演示
    count = 0
    for event in timeline:
        if count >= 10: break
        
        notes = event['notes'] # JSON string or list
        if isinstance(notes, str):
            notes = json.loads(notes)
            
        if not notes: continue # 跳过休止符
        
        # 复制一份底图
        frame = ref_img.copy()
        
        # 在图上画信息
        info_text = f"Time: {event['time']} | Chord: {event['chord']}"
        cv2.putText(frame, info_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        # 画指位
        for note in notes:
            string_idx = note['string'] - 1 # DB存的是1-6, 我们代码通常用0-5
            fret_idx = note['fret']
            
            # 获取像素坐标
            # 注意：这里直接用 reference grid 的坐标，假设摄像头视角就是参考图视角
            # 在直播模式下，这里会用到 Homography 变换
            coords = grid_system.get_coords(string_idx, fret_idx)
            
            if coords:
                x, y = coords
                # 画一个绿色的实心圆代表手指按的位置
                cv2.circle(frame, (int(x), int(y)), 15, (0, 255, 0), -1)
                # 画品格文字
                cv2.putText(frame, str(fret_idx), (int(x)-10, int(y)+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # 保存图片
        filename = f"{output_dir}/frame_{count:03d}_time_{event['time']}.jpg"
        cv2.imwrite(filename, frame)
        print(f"   -> Saved {filename}")
        count += 1

    print(f"✅ 可视化完成！请查看 {output_dir} 文件夹。")

if __name__ == "__main__":
    visualize_song_from_db()

