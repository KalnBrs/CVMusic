from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
from NotePositions.Vector2 import Vector2
from NotePositions.GetNotePosition import get_chord_positions

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

    data = await frame.read()
    nparr = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Get corners of fretboard (stubbed for now)
    c1 = Vector2(100, 100)
    c2 = Vector2(500, 100)
    c3 = Vector2(80, 400)
    c4 = Vector2(520, 400)

    # Get note positions for the chord
    notes = get_chord_positions(chord_tab, c1, c2, c3, c4)

    positions = []
    for note in notes:
        if hasattr(note, "x") and hasattr(note, "y"):
            x, y = note.x, note.y
        elif isinstance(note, (list, tuple, np.ndarray)) and len(note) >= 2:
            x, y = note[0], note[1]
        else:
            continue
        try:
            positions.append({"x": int(round(float(x))), "y": int(round(float(y)))})
        except Exception:
            continue

    return {"notes": positions}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)