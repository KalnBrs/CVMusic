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

#### 🌐 API Server (Coming Soon)
```bash
python api_server.py
```

## 📂 Project Structure

- **`database_manager.py`**: Core script for DB connections, schema creation, and data import.
- **`dataset_seeder.py`**: Generates `.tokens.txt` files for the dataset.
- **`fretboard_tracker.py`**: CV logic for tracking the guitar neck using SIFT/Homography.
- **`mediapipe_finger_detection.py`**: Wrapper for Google's MediaPipe Hands.
- **`grid_detection.py`**: Algorithms for detecting strings and frets.
- **`reference_grid.json`**: Calibration data for the guitar neck.

## 🛠 Troubleshooting

- **Permission Denied (DB)**: If you get schema permission errors, run:
  ```bash
  psql -h ec2-54-91-59-31.compute-1.amazonaws.com -U kaelanbrose -d cv_db -W -c "GRANT ALL ON SCHEMA public TO kaelanbrose;"
  ```
- **Missing `song_data`**: Ensure you ran `python dataset_seeder.py` first.
