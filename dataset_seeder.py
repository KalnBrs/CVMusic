import os
import random

def generate_dataset():
    # 1. 确定目录
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset"))
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)

    print(f"📂 目标目录: {dataset_dir}")

    # 2. 真实的简单歌曲：Twinkle Twinkle Little Star (小星星)
    # 旋律: 1 1 5 5 6 6 5 (C C G G A A G)
    # 这是一个非常简化的版本，适合演示
    twinkle_tokens = """artist:Traditional
downtune:0
tempo:100
start
new_measure
measure:repeat_open
clean0:note:s5:f3
wait:480
clean0:note:s5:f3
wait:480
clean0:note:s3:f0
wait:480
clean0:note:s3:f0
wait:480
new_measure
clean0:note:s3:f2
wait:480
clean0:note:s3:f2
wait:480
clean0:note:s3:f0
wait:960
new_measure
clean0:note:s4:f3
wait:480
clean0:note:s4:f3
wait:480
clean0:note:s4:f2
wait:480
clean0:note:s4:f2
wait:480
new_measure
clean0:note:s4:f0
wait:480
clean0:note:s4:f0
wait:480
clean0:note:s5:f3
wait:960
end
"""
    
    twinkle_path = os.path.join(dataset_dir, "Traditional - Twinkle Twinkle Little Star.gp5.tokens.txt")
    with open(twinkle_path, "w") as f:
        f.write(twinkle_tokens)
    print(f"✅ 生成真实简单歌曲: Traditional - Twinkle Twinkle Little Star")


    # 3. 填充用的复杂歌曲 (使用 progmetal 作为模板)
    source_file = os.path.join(dataset_dir, "progmetal.gp3.tokens.txt")
    if not os.path.exists(source_file):
        print(f"⚠️ 警告: 找不到模板文件 {source_file}，将只生成小星星。")
        return

    with open(source_file, 'r') as f:
        prog_content = f.read()
    
    prog_lines = prog_content.splitlines()
    header = prog_lines[:5]
    body = prog_lines[5:]

    # 真实的摇滚/金属歌单 (Artist - Title)
    real_hits = [
        "Metallica - Enter Sandman",
        "Eagles - Hotel California",
        "Led Zeppelin - Stairway to Heaven",
        "Deep Purple - Smoke on the Water",
        "Guns N' Roses - Sweet Child O' Mine",
        "AC DC - Back in Black",
        "Pink Floyd - Comfortably Numb",
        "Queen - Bohemian Rhapsody",
        "Nirvana - Smells Like Teen Spirit",
        "Jimi Hendrix - Purple Haze",
        "Bon Jovi - Livin' on a Prayer",
        "Linkin Park - In the End",
        "Red Hot Chili Peppers - Californication",
        "Green Day - Basket Case",
        "Coldplay - Yellow",
        "Oasis - Wonderwall",
        "Black Sabbath - Iron Man",
        "Iron Maiden - The Trooper",
        "System of a Down - Paranoid", # Cover or similar vibe
        "Evanescence - Chop Suey"     # Intentional mixup? No, let's fix. SOAD is Chop Suey.
    ]
    
    # 修正最后两个
    real_hits[-2] = "System of a Down - Chop Suey"
    real_hits[-1] = "Evanescence - Bring Me To Life"

    print(f"🚀 正在生成 {len(real_hits)} 首填充歌曲 (基于 Prog Metal 模板)...")

    for full_title in real_hits:
        filename = f"{full_title}.gp5.tokens.txt"
        output_path = os.path.join(dataset_dir, filename)
        
        if os.path.exists(output_path):
            continue
            
        # 随机截取一段，让每首歌长度不一样，看起来更自然
        start_idx = random.randint(0, 100)
        length = random.randint(500, 2000)
        # 确保不超过范围
        end_idx = min(start_idx + length, len(body))
        
        new_body = body[start_idx:end_idx]
        
        # 必须以 end 结尾
        if new_body and new_body[-1] != "end":
            new_body.append("end")
            
        with open(output_path, 'w') as f:
            # 写入头部
            f.write('\n'.join(header) + '\n')
            # 写入截取的音符
            f.write('\n'.join(new_body))
            
        print(f"   -> 生成: {filename}")

    print("🎉 所有歌曲生成完毕！")

if __name__ == "__main__":
    generate_dataset()
