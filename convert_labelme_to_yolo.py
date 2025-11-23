import os
import json
import glob
import shutil
import numpy as np

# ================= CONFIG =================
# 数据集根目录
DATASET_ROOT = "datasets"
# 关键点顺序 (对应 YOLO 中的 index 0, 1, 2, 3)
# 假设顺序: [琴头-粗弦(TL), 琴头-细弦(TR), 琴身-细弦(BR), 琴身-粗弦(BL)]
KEYPOINT_LABELS = ["TL", "TR", "BR", "BL"]
# ==========================================

def convert_dataset(split):
    """
    转换 train 或 val 数据集
    split: 'train' or 'val'
    """
    json_dir = os.path.join(DATASET_ROOT, "images", split)
    label_dir = os.path.join(DATASET_ROOT, "labels", split)
    
    # 确保 label 目录存在
    if os.path.exists(label_dir):
        shutil.rmtree(label_dir)
    os.makedirs(label_dir)
    
    json_files = glob.glob(os.path.join(json_dir, "*.json"))
    print(f"Found {len(json_files)} json files in {split} set.")
    
    count = 0
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            img_h = data['imageHeight']
            img_w = data['imageWidth']
            
            # 1. 提取关键点和 BBox
            keypoints = {} # label -> (x, y)
            points_list = [] # 用于计算 bbox 如果没有画框
            bbox = None
            
            for shape in data['shapes']:
                label = shape['label']
                points = shape['points']
                shape_type = shape['shape_type']
                
                if shape_type == 'rectangle' or label == 'fretboard':
                    # 如果画了框
                    (x1, y1), (x2, y2) = points
                    bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
                
                elif shape_type == 'point':
                    # 如果是点
                    x, y = points[0]
                    keypoints[label] = (x, y)
                    points_list.append((x, y))
            
            # 如果没有明确的 bbox，根据点生成一个外接矩形 (稍微扩大一点)
            if bbox is None:
                if not points_list:
                    print(f"Skipping {json_file}: No points found.")
                    continue
                pts = np.array(points_list)
                min_x, min_y = np.min(pts, axis=0)
                max_x, max_y = np.max(pts, axis=0)
                # 增加 10% 的 padding
                pad_x = (max_x - min_x) * 0.1
                pad_y = (max_y - min_y) * 0.1
                bbox = [
                    max(0, min_x - pad_x), 
                    max(0, min_y - pad_y), 
                    min(img_w, max_x + pad_x), 
                    min(img_h, max_y + pad_y)
                ]
                
            # 2. 整理关键点顺序
            # 如果用户用了标准 Label (TL, TR...)
            final_kps = []
            
            # 检查是否使用了预定义的 label
            if any(l in keypoints for l in KEYPOINT_LABELS):
                for target_label in KEYPOINT_LABELS:
                    if target_label in keypoints:
                        final_kps.append(keypoints[target_label])
                    else:
                        # 如果缺了某个点，设为 0,0 (不可见)
                        final_kps.append((0, 0))
            else:
                # 如果没用 Label (或者是自动生成的 label)，就按点的顺序 (假设用户是按顺序点的)
                # 或者简单的按 y 坐标排序? 不，这太冒险。
                # 我们假设如果没 label，就取前 4 个点
                # print(f"Warning: {json_file} uses non-standard labels: {list(keypoints.keys())}. Using raw order.")
                # 简单的把所有点拿出来
                raw_points = points_list[:4]
                # 补齐 4 个
                while len(raw_points) < 4:
                    raw_points.append((0, 0))
                final_kps = raw_points

            # 3. 转换为 YOLO 格式
            # <class-index> <x_center> <y_center> <width> <height> <px1> <py1> <vis1> <px2> <py2> <vis2> ...
            
            # BBox normalization
            bx1, by1, bx2, by2 = bbox
            bw = bx2 - bx1
            bh = by2 - by1
            xc = bx1 + bw / 2.0
            yc = by1 + bh / 2.0
            
            norm_xc = xc / img_w
            norm_yc = yc / img_h
            norm_w = bw / img_w
            norm_h = bh / img_h
            
            line_str = f"0 {norm_xc:.6f} {norm_yc:.6f} {norm_w:.6f} {norm_h:.6f}"
            
            for kp in final_kps:
                kx, ky = kp
                # 归一化
                nkx = kx / img_w
                nky = ky / img_h
                # vis = 2 (visible and labeled) if not (0,0) else 0
                vis = 2 if (kx != 0 or ky != 0) else 0
                line_str += f" {nkx:.6f} {nky:.6f} {vis}"
            
            # 写入 TXT
            txt_filename = os.path.splitext(os.path.basename(json_file))[0] + ".txt"
            txt_path = os.path.join(label_dir, txt_filename)
            
            with open(txt_path, 'w') as f_out:
                f_out.write(line_str + "\n")
                
            count += 1
            
        except Exception as e:
            print(f"Error converting {json_file}: {e}")

    print(f"Success: Converted {count} files for {split}.")

if __name__ == "__main__":
    convert_dataset('train')
    convert_dataset('val')

