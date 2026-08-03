import os
import base64
import numpy as np
import cv2
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from utils import analyze_frame_with_mediapipe

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.get_json()
        image_data = data['image']
        
        # Strip the data URL prefix if present (e.g., "data:image/jpeg;base64,...")
        if ',' in image_data:
            image_data = image_data.split(',')[1]
            
        # Decode base64 image
        decoded_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(decoded_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"status": "error", "message": "Invalid frame data"}), 400

        # Pass frame through MediaPipe AI analysis
        current_reps, form_message = analyze_frame_with_mediapipe(frame)
        
        return jsonify({
            "status": "success",
            "reps": current_reps,
            "form": form_message
        })

    except Exception as e:
        print(f"Error processing frame: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)