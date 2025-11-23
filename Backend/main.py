from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
from FretboardDetection.GetFretboardCorners import get_fretboard_corners
from Vector2 import Vector2
from NotePositions.GetNotePosition import get_chord_positions
import json

app = FastAPI()

# Allow CORS from React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process_frame")
async def process_frame(frame: UploadFile = File(...),
                        chord_tab: str = Form(None)):
    
    print("Received file:", frame.filename)
    print("Received chord tab:", chord_tab)

    # Convert chord_tab string to list
    if chord_tab is None:
        chord_tab_list = []
    else:
        try:
            chord_tab_list = json.loads(chord_tab)
        except json.JSONDecodeError:
            return {"error": "Invalid chord_tab format, must be JSON list of frets."}

    data = await frame.read()
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    corners = get_fretboard_corners(img)

    if not corners:
        return {"error": "No fretboard corners detected."}

    # Get note positions for the chord
    notes = get_chord_positions(chord_tab_list, corners[0], corners[1], corners[2], corners[3])

    positions = []
    for note in notes:
        if note is None:
            positions.append(None)
            continue
        if hasattr(note, "x") and hasattr(note, "y"):
            x, y = note.x, note.y
        elif isinstance(note, (list, tuple, np.ndarray)) and len(note) >= 2:
            x, y = note[0], note[1]
        else:
            positions.append(None)
            continue
        positions.append({"x": int(round(float(x))), "y": int(round(float(y)))})

    return {"notes": positions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)