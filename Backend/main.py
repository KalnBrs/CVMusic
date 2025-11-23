from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import json
from FretboardDetection.GetFretboardCorners import get_fretboard_corners
from NotePositions.GetNotePosition import get_chord_positions
from HandDetection.FingerDetector import FingerDetector
from Verification.Verifier import verify_chord_placement

app = FastAPI()

# Initialize Finger Detector
finger_detector = FingerDetector()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def preprocess_image(file_bytes):
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Could not decode image.")

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    img = img.astype(np.uint8)
    img = cv2.resize(img, (640, 480))
    return img

@app.post("/api/process_frame")
async def process_frame(frame: UploadFile = File(...), chord_tab: str = Form(None)):
    chord_tab_list = []
    if chord_tab:
        try:
            chord_tab_list = json.loads(chord_tab)
            if not isinstance(chord_tab_list, list):
                raise ValueError("chord_tab must be a list")
        except Exception as e:
            return {"error": f"Invalid chord_tab format: {str(e)}"}

    data = await frame.read()
    try:
        img = preprocess_image(data)
    except Exception as e:
        return {"error": f"Failed to process image: {str(e)}"}

    corners_raw = get_fretboard_corners(img)
    if not corners_raw:
        return {"error": "No fretboard corners detected."}

    corners = {
        "TL": {"x": int(round(float(corners_raw[0].x))), "y": int(round(float(corners_raw[0].y)))},
        "TR": {"x": int(round(float(corners_raw[1].x))), "y": int(round(float(corners_raw[1].y)))},
        "BL": {"x": int(round(float(corners_raw[2].x))), "y": int(round(float(corners_raw[2].y)))},
        "BR": {"x": int(round(float(corners_raw[3].x))), "y": int(round(float(corners_raw[3].y)))},
    }

    # Correctly reverse chord_tab_list if needed
    # chord_tab_list = chord_tab_list[::-1]

    # Make sure corner order matches get_chord_positions expectations
    notes_raw = get_chord_positions(chord_tab_list, corners_raw[2], corners_raw[1], corners_raw[3], corners_raw[0])

    notes = []
    for note in notes_raw:
        if note is None:
            notes.append(None)
            continue
        try:
            x, y = (note.x, note.y) if hasattr(note, "x") else (note[0], note[1])
            notes.append({"x": int(round(float(x))), "y": int(round(float(y)))})
        except Exception:
            notes.append(None)

    # Detect Fingertips
    fingertips_raw = finger_detector.detect(img)
    
    # Filter fingertips based on fretboard region
    # Define a polygon from corners: TL -> TR -> BR -> BL
    # corners_raw is tuple of Vector2: 0=TL, 1=TR, 2=BL, 3=BR (Wait, check GetFretboardCorners return order)
    # get_fretboard_corners returns tuple(points). Let's check what points is.
    # It sorts them? Usually Y-sorted or X-sorted.
    # In main.py: 
    # "TL": corners_raw[0], "TR": corners_raw[1], "BL": corners_raw[2], "BR": corners_raw[3]
    # This assumes a specific order. Let's assume the Polygon is 0 -> 1 -> 3 -> 2 (TL -> TR -> BR -> BL)
    
    fretboard_poly = np.array([
        [corners_raw[0].x, corners_raw[0].y], # TL
        [corners_raw[1].x, corners_raw[1].y], # TR
        [corners_raw[3].x, corners_raw[3].y], # BR
        [corners_raw[2].x, corners_raw[2].y]  # BL
    ], dtype=np.int32)

    fingertips_list = []
    for ft in fingertips_raw:
        # Measure distance to polygon. Positive = inside, Negative = outside.
        # Allow a margin of 50 pixels around the fretboard
        dist = cv2.pointPolygonTest(fretboard_poly, (float(ft[0]), float(ft[1])), True)
        if dist >= -50.0: 
            fingertips_list.append(ft)

    # Convert to dict for JSON response
    detected_fingers = [{"x": x, "y": y} for x, y in fingertips_list]

    # Verify Placement
    verification = verify_chord_placement(notes, fingertips_list)

    return {"notes": notes, "corners": corners, "detected_fingers": detected_fingers, "verification": verification}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
