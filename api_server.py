  from flask import Flask, request, jsonify
  from flask_cors import CORS
  import base64, cv2, numpy as np
  from mediapipe_finger_detection import FingerAnalyzer, ExpectedPosition

    app = Flask(__name__)
  CORS(app)
  analyzer = FingerAnalyzer()

  def decode_image(image_str: str) -> np.ndarray:
      if image_str.startswith("data:image"):
          image_str = image_str.split(",", 1)[1]
      img_bytes = base64.b64decode(image_str)
      img_array = np.frombuffer(img_bytes, dtype=np.uint8)
      img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
      return img

  @app.post("/analyze_frame")
  def analyze_frame():
      data = request.get_json() or {}
      image_str = data.get("image")
      if not image_str:
          return jsonify({"success": False, "error": "no image"}), 400

      img = decode_image(image_str)

      expected_raw = data.get("expected") or []
      expected = []
      for pos in expected_raw:
          try:
              expected.append(
                  ExpectedPosition(string=int(pos["string"]), fret=int(pos["fret"]))
              )
          except (KeyError, ValueError):
              continue

      result = analyzer.analyze(img, expected_positions=expected or None)
      return jsonify(result)