import psycopg2
import json
import os
import re

class DatabaseManager:
    def __init__(self):
        # 数据库连接配置
        self.host = "ec2-54-91-59-31.compute-1.amazonaws.com"
        self.database = "cv_db"
        self.user = "kaelanbrose"
        self.password = os.getenv("DB_PASSWORD", "May221927$") 
        self.port = "5432"
        self.conn = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            print("✅ 数据库连接成功")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"❌ 连接数据库失败: {error}")
            self.conn = None

    def close(self):
        if self.conn is not None:
            self.conn.close()
            print("数据库连接已关闭")

    def initialize_schema(self):
        """初始化三张核心表：songs, song_chords, chord_voicings"""
        if not self.conn:
            self.connect()
            if not self.conn: return

        # 1. Songs 表：存储歌曲元数据
        create_songs_table = """
        CREATE TABLE IF NOT EXISTS songs (
            id SERIAL PRIMARY KEY,
            title VARCHAR(100),
            artist VARCHAR(100),
            created_at TIMESTAMP DEFAULT now()
        );
        """

        # 2. Song Chords 表：存储时间轴上的和弦/事件
        # 我们额外加一个 exact_notes 字段，存储具体的六线谱按法，这对 CV 来说比 chord_name 更直接
        create_song_chords_table = """
        CREATE TABLE IF NOT EXISTS song_chords (
            id SERIAL PRIMARY KEY,
            song_id INT REFERENCES songs(id) ON DELETE CASCADE,
            measure_index INT,      -- 第几小节
            beat_time INT,          -- 在歌曲中的绝对时间（tick）或者小节内的偏移
            chord_name VARCHAR(20), -- 识别出的和弦名 (如 "Em", "C")
            exact_notes JSONB       -- 具体的按法: [{"string": 6, "fret": 0}, ...]
        );
        """

        # 3. Chord Voicings 表：标准和弦指法字典 (CV 的 Ground Truth)
        create_chord_voicings_table = """
        CREATE TABLE IF NOT EXISTS chord_voicings (
            id SERIAL PRIMARY KEY,
            chord_name VARCHAR(20),
            string INT,
            fret INT,
            UNIQUE(chord_name, string)
        );
        """

        try:
            cur = self.conn.cursor()
            cur.execute(create_songs_table)
            cur.execute(create_song_chords_table)
            cur.execute(create_chord_voicings_table)
            
            self.conn.commit()
            cur.close()
            print("✅ 表结构初始化完成 (songs, song_chords, chord_voicings)。")
            
            # 顺便初始化一些标准和弦字典
            self.seed_chord_voicings()
            
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"❌ 初始化失败: {error}")
            self.conn.rollback()

    def seed_chord_voicings(self):
        """预填一些常用和弦的标准指法"""
        common_chords = {
            "Em": [(6,0), (5,2), (4,2), (3,0), (2,0), (1,0)],
            "E":  [(6,0), (5,2), (4,2), (3,1), (2,0), (1,0)],
            "Am": [(5,0), (4,2), (3,2), (2,1), (1,0)],
            "C":  [(5,3), (4,2), (3,0), (2,1), (1,0)],
            "G":  [(6,3), (5,2), (4,0), (3,0), (2,0), (1,3)],
            "D":  [(4,0), (3,2), (2,3), (1,2)],
            "F":  [(6,1), (5,3), (4,3), (3,2), (2,1), (1,1)], # Bar chord
            "E5": [(6,0), (5,2), (4,2)], # Power chord
            "A5": [(5,0), (4,2), (3,2)], # Power chord
            "D5": [(4,0), (3,2)],
        }
        
        cur = self.conn.cursor()
        try:
            for name, notes in common_chords.items():
                # 先删除旧的定义，防止重复累积
                cur.execute("DELETE FROM chord_voicings WHERE chord_name = %s", (name,))
                for s, f in notes:
                    cur.execute(
                        "INSERT INTO chord_voicings (chord_name, string, fret) VALUES (%s, %s, %s)",
                        (name, s, f)
                    )
            self.conn.commit()
            print("✅ 标准和弦字典已更新。")
        except Exception as e:
            print(f"❌ 写入和弦字典失败: {e}")
            self.conn.rollback()
        finally:
            cur.close()

    def import_token_file(self, filepath, title="Unknown Song", artist="Unknown Artist"):
        """
        解析 .tokens.txt 文件并存入数据库
        """
        if not self.conn: self.connect()
        
        print(f"🚀 开始解析文件: {filepath}")
        
        # 1. 创建歌曲记录
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO songs (title, artist) VALUES (%s, %s) RETURNING id",
            (title, artist)
        )
        song_id = cur.fetchone()[0]
        print(f"   -> 创建歌曲 ID: {song_id}")

        # 2. 解析文件内容
        events = []
        current_measure = 1
        current_time = 0
        note_buffer = [] # 存储当前时间点（拍）内的所有音符
        
        with open(filepath, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            parts = line.split(':')
            
            if not parts: continue
            
            # 处理小节线
            if "new_measure" in line:
                current_measure += 1
                continue
                
            # 处理等待 (时间前进)，这意味着一个“拍”或“事件”结束了
            if parts[0] == "wait":
                duration = int(parts[1])
                
                if note_buffer:
                    # 这一拍有音符，将其作为一个事件保存
                    chord_name = self.identify_chord(note_buffer)
                    events.append({
                        "song_id": song_id,
                        "measure_index": current_measure,
                        "beat_time": current_time,
                        "chord_name": chord_name,
                        "exact_notes": json.dumps(note_buffer)
                    })
                    note_buffer = [] # 清空 buffer 准备下一拍
                
                current_time += duration
                continue
            
            # 处理音符: e.g., distorted0:note:s4:f2
            if len(parts) >= 4 and parts[1] == "note":
                # 解析 string (sX) 和 fret (fX)
                try:
                    string_str = parts[2] # s4
                    fret_str = parts[3]   # f2
                    
                    string_idx = int(string_str.replace('s', ''))
                    fret_idx = int(fret_str.replace('f', ''))
                    
                    note_buffer.append({"string": string_idx, "fret": fret_idx})
                except:
                    pass # 忽略解析错误的行

        # 3. 批量写入数据库
        print(f"   -> 解析出 {len(events)} 个事件，正在写入数据库...")
        
        for ev in events:
            cur.execute("""
                INSERT INTO song_chords (song_id, measure_index, beat_time, chord_name, exact_notes)
                VALUES (%s, %s, %s, %s, %s)
            """, (ev['song_id'], ev['measure_index'], ev['beat_time'], ev['chord_name'], ev['exact_notes']))
            
        self.conn.commit()
        cur.close()
        print("✅ 导入完成！")

    def identify_chord(self, notes):
        """
        简单的和弦识别逻辑 (Rule-based)
        notes: list of {'string': s, 'fret': f}
        """
        if not notes: return None
        
        # 简单的 Power Chord 识别 (只看根音)
        # 这里只是一个极其简化的示例，实际可以做更复杂的匹配
        
        # 提取所有 (string, fret) 对用于匹配
        current_shape = set((n['string'], n['fret']) for n in notes)
        
        # 1. 尝试匹配 E5 (Open E power chord)
        # E5 通常是 6弦0品, 5弦2品, 4弦2品
        e5_shape = {(6,0), (5,2), (4,2)}
        if e5_shape.issubset(current_shape): return "E5"
        
        # 2. 尝试匹配 A5 (Open A power chord)
        a5_shape = {(5,0), (4,2), (3,2)}
        if a5_shape.issubset(current_shape): return "A5"
        
        # 3. 尝试匹配 D5
        d5_shape = {(4,0), (3,2)}
        if d5_shape.issubset(current_shape): return "D5"

        # 如果只是单音或者不认识的和弦，暂时返回 None 或 'Unknown'
        return "Unknown"

    def get_song_timeline(self, song_id):
        """获取某首歌的完整时间轴"""
        if not self.conn: self.connect()
        cur = self.conn.cursor()
        cur.execute("""
            SELECT measure_index, beat_time, chord_name, exact_notes 
            FROM song_chords 
            WHERE song_id = %s 
            ORDER BY beat_time ASC
        """, (song_id,))
        rows = cur.fetchall()
        cur.close()
        return [
            {
                "measure": r[0],
                "time": r[1],
                "chord": r[2],
                "notes": r[3]
            } for r in rows
        ]

    def import_all_from_directory(self, directory_path):
        """
        批量导入指定目录下的所有 .tokens.txt 文件
        """
        if not os.path.exists(directory_path):
            print(f"❌ 目录不存在: {directory_path}")
            return

        files = [f for f in os.listdir(directory_path) if f.endswith(".tokens.txt")]
        print(f"📂 在 {directory_path} 中找到 {len(files)} 个乐谱文件。")

        count = 0
        for filename in files:
            filepath = os.path.join(directory_path, filename)
            
            # 从文件名推测歌名 (去除 .gpX.tokens.txt 后缀)
            # 例如: "Metallica - One.gp5.tokens.txt" -> "Metallica - One"
            title = filename.split('.gp')[0].replace('_', ' ')
            artist = "Unknown" 
            if " - " in title:
                parts = title.split(" - ")
                artist = parts[0]
                title = parts[1]
            
            # 检查是否已存在
            cur = self.conn.cursor()
            cur.execute("SELECT id FROM songs WHERE title = %s AND artist = %s", (title, artist))
            if cur.fetchone():
                print(f"⏭️  跳过已存在: {title}")
                cur.close()
                continue
            cur.close()

            try:
                self.import_token_file(filepath, title=title, artist=artist)
                count += 1
            except Exception as e:
                print(f"❌ 导入 {filename} 失败: {e}")

        print(f"🎉 批量导入完成！成功导入 {count} 首新歌。")

if __name__ == "__main__":
    import sys
    db = DatabaseManager()
    
    if len(sys.argv) > 1:
        db.password = sys.argv[1]
    
    # 1. 初始化表 (如果还没初始化)
    db.initialize_schema()
    
    # 2. 批量导入 dataset 目录下的所有歌曲
    dataset_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset"))
    db.import_all_from_directory(dataset_dir)
        
    db.close()
