# CVMusic - AI Guitar Chord Assistant

This project is a computer vision-based application that helps users learn guitar chords by detecting the fretboard and finger positions in real-time. It consists of three parts: a Python Backend (CV processing), a Node.js Backend API, and a React Frontend.

## Prerequisites

- **Python 3.11** (Required for MediaPipe compatibility on macOS Apple Silicon)
- **Node.js** (v16 or higher recommended)
- **npm**

## Setup Instructions

### 1. Python Backend (Computer Vision)

This service handles image processing, fretboard detection, and finger detection.

1.  Navigate to the project root directory.
2.  Create a virtual environment using Python 3.11:
    ```bash
    python3.11 -m venv venv
    ```
    *(Note: Ensure you are using Python 3.11 specifically, as MediaPipe wheels for Apple Silicon are most stable on this version.)*

3.  Activate the virtual environment:
    - On macOS/Linux: `source venv/bin/activate`
    - On Windows: `venv\Scripts\activate`

4.  Install the required dependencies:
    ```bash
    pip install --upgrade pip
    pip install fastapi uvicorn opencv-python numpy mediapipe ultralytics python-multipart torch torchvision torchaudio
    ```

### 2. Backend API (Node.js)

This service manages application logic and data.

1.  Navigate to the `Backend-API` directory:
    ```bash
    cd Backend-API
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```

### 3. Frontend (React/Vite)

The user interface for the application.

1.  Navigate to the `Frontend` directory:
    ```bash
    cd Frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```

## Running the Application

You need to run all three services simultaneously in separate terminal windows.

### Terminal 1: Python Backend
From the **project root** directory:
```bash
# Set PYTHONPATH to include the Backend directory and start the server
export PYTHONPATH=$PYTHONPATH:$(pwd)/Backend
source venv/bin/activate
python -m uvicorn Backend.main:app --reload --host 0.0.0.0 --port 3000
```
*The Python backend will run on port 3000.*

### Terminal 2: Backend API
From the `Backend-API` directory:
```bash
npm start
```
*The API server will typically run on port 8000.*

### Terminal 3: Frontend
From the `Frontend` directory:
```bash
npm run dev
```
*The frontend will usually run on http://localhost:5173 (or 5174 if 5173 is busy).*

## Usage

1.  Open your browser and navigate to the URL shown in the Frontend terminal (e.g., `http://localhost:5173`).
2.  Go to the "Cam Setup" or "Chord Explore" page.
3.  Allow camera access when prompted.
4.  Position your guitar fretboard in the camera view. The system will detect the fretboard corners (visualized on screen) and your finger positions (filtered to show only those on the fretboard).

