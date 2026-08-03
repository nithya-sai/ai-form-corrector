import os
import base64
import numpy as np
import cv2
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from utils import analyze_frame_with_mediapipe  # Imports your core AI logic from utils.py

app = Flask(__name__)

# Configure upload folder for recorded videos
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

# Route 1: Handle Pre-recorded Video Uploads
@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Here you can process your uploaded video file if needed
        return render_template('index.html', message="Video processed successfully!")

# Route 2: Handle Real-Time Frames from Mobile/PC Browser Cameras
@app.route('/process_frame', methods=['POST'])
def process_frame():
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({"status": "error", "message": "No image data received"}), 400

        # 1. Strip the base64 header and convert to numpy array
        encoded_data = image_data.split(',')[1]
        nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
        
        # 2. Decode into an OpenCV frame matrix
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"status": "error", "message": "Failed to decode frame"}), 400

        # 3. Pass the live frame through your MediaPipe/AI model
        current_reps, form_message = analyze_frame_with_mediapipe(frame)

        # 4. Return live feedback back to the mobile browser
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