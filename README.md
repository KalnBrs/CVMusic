# CVMusic Backend

This is the backend service for the CVMusic guitar teaching system. It handles:
1.  **Computer Vision**: Detecting guitar fretboard and finger positions using OpenCV and MediaPipe.
2.  **Database**: Managing songs, chords, and tablature data using PostgreSQL (AWS RDS).
3.  **API**: Serving analysis results and song data to the frontend.

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.11** (Recommended to use `pyenv`)
- **PostgreSQL** (Client tools mostly, server is on AWS)

### 2. Environment Setup

Since `venv` is excluded from git, you need to create it locally:

```bash
# 1. Create virtual environment
cd Backend
python -m venv venv

# 2. Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### 3. Database Configuration

The backend connects to an AWS RDS PostgreSQL instance. You need to set the password via an environment variable or manually input it when prompted.

**Credentials:**
- Host: `ec2-54-91-59-31.compute-1.amazonaws.com`
- User: `kaelanbrose`
- Database: `cv_db`
- Password: *(Ask the team lead if you don't have it)*

To set the password temporarily for your session:
```bash
export DB_PASSWORD="YOUR_PASSWORD_HERE"
```

### 4. Initialize & Populate Data (The "Seeding" Process)

To get the system ready with songs and chords:

**Step A: Generate Dataset Files**
Creates song token files (including "Twinkle Twinkle Little Star" and other rock hits) in the `../dataset` folder.
```bash
python dataset_seeder.py
```

**Step B: Initialize DB & Import Songs**
Creates tables (`songs`, `song_chords`, `chord_voicings`) and imports all files from `dataset/` into the AWS database.
```bash
python database_manager.py
```
*Note: If you didn't export `DB_PASSWORD`, you can pass it as an argument: `python database_manager.py YOUR_PASSWORD`*

### 5. Running the System

#### 🎸 Live CV Demo (Webcam)
To see the fretboard tracking and finger detection in action:
```bash
python demo_webcam_live.py
```
*Ensure you have `reference_neck.jpg` and `reference_grid.json` in the Backend folder.*

#### 📊 Visualization Debugger
To visualize a song from the database onto the static reference image:
```bash
python visualize_db_song.py
```

## 🏋️ Training the Fretboard Model (YOLOv8 Pose)

If you have a GPU (NVIDIA is best, but Mac M1/M2 works too), you can train the Keypoint Detection model.

### 1. Install Additional Dependencies
```bash
pip install ultralytics labelme
```

### 2. Data Preparation
1.  Put your training videos in `Backend/` (e.g., `guitar_train.mp4`).
2.  Run the dataset preparation script to extract frames:
    ```bash
    python prepare_dataset.py
    ```
    *(This creates `datasets/images/train` and `datasets/images/val`)*

### 3. Annotation (Labelme)
1.  Run `labelme` in your terminal.
2.  Open `Backend/datasets/images/train`.
3.  **Annotate following this STRICT order**:
    -   Draw a **Rectangle** around the fretboard -> Label: `fretboard`
    -   Create **Points** in this exact order:
        1.  **Top-Left (TL)**: Headstock - Thick String
        2.  **Top-Right (TR)**: Headstock - Thin String
        3.  **Bottom-Right (BR)**: Body - Thin String
        4.  **Bottom-Left (BL)**: Body - Thick String
    -   Save the JSON file.

### 4. Convert Data & Train
1.  **Convert Labelme JSON to YOLO TXT**:
    ```bash
    python convert_labelme_to_yolo.py
    ```
2.  **Start Training**:
    ```bash
    python train_yolo_pose.py
    ```
    *(Results will be saved in `runs/pose/fretboard_v1/weights/best.pt`)*

## 📂 Project Structure

- **`database_manager.py`**: Core script for DB connections, schema creation, and data import.
- **`dataset_seeder.py`**: Generates `.tokens.txt` files for the dataset.
- **`fretboard_tracker.py`**: CV logic for tracking the guitar neck using SIFT/Homography.
- **`mediapipe_finger_detection.py`**: Wrapper for Google's MediaPipe Hands.
- **`grid_detection.py`**: Algorithms for detecting strings and frets.
- **`reference_grid.json`**: Calibration data for the guitar neck.
- **`train_yolo_pose.py`**: Script to train the Keypoint Detection model.

## 🛠 Troubleshooting

- **Permission Denied (DB)**: If you get schema permission errors, run:
  ```bash
  psql -h ec2-54-91-59-31.compute-1.amazonaws.com -U kaelanbrose -d cv_db -W -c "GRANT ALL ON SCHEMA public TO kaelanbrose;"
  ```
- **Missing `song_data`**: Ensure you ran `python dataset_seeder.py` first.
