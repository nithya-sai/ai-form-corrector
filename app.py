import os
from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_frames(video_source):
    # video_source will be 0 (for webcam) or a file path (for uploads)
    cap = cv2.VideoCapture(video_source)
    
    counter = 0 
    stage = "down"
    feedback = "Processing Form"
    
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
            
        # Flip the frame horizontally ONLY if it is a live webcam feed
        if video_source == 0:
            frame = cv2.flip(frame, 1)
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            center_y = y + (h // 2)
            
            if center_y > 220:
                stage = "down"
                feedback = "Form: Range clear"
            elif center_y < 150 and stage == "down":
                stage = "up"
                counter += 1
                feedback = "Rep Counted!"
            
            cv2.circle(frame, (x + w//2, center_y), 8, (0, 0, 255), -1)
            
        cv2.rectangle(frame, (0, 0), (640, 70), (30, 30, 30), -1)
        cv2.putText(frame, 'REPS', (15, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, str(counter), (15, 58), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        cv2.putText(frame, 'STAGE', (120, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, str(stage).upper(), (120, 58), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        cv2.putText(frame, 'FEEDBACK', (280, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, feedback, (280, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/', methods=['GET', 'POST'])
def index():
    # Detect what mode the user wants to be in
    video_type = request.args.get('mode', 'none')
    video_file = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Set variables to render the uploaded video
            video_file = filename
            video_type = 'upload'
            return render_template('index.html', video_type=video_type, video_file=video_file)
            
    return render_template('index.html', video_type=video_type, video_file=None)

# Route for Live Webcam
@app.route('/live_feed')
def live_feed():
    return Response(generate_frames(0), mimetype='multipart/x-mixed-replace; boundary=frame')

# Route for Uploaded Videos
@app.route('/video_feed/<filename>')
def video_feed(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return Response(generate_frames(filepath), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, port=5000)