import subprocess
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This allows your React frontend to communicate with this backend

# Storage for the logs shown in your Intel Feed
detections = []

# Define the absolute path to your Python executable
PYTHON_EXE = "C:/Users/Sindhu Kallakuri/AppData/Local/Programs/Python/Python313/python.exe"
# Define the absolute path to your backend directory
BACKEND_DIR = "C:/Users/Sindhu Kallakuri/OneDrive/Desktop/Aarani/backend"

@app.route('/api/logs', methods=['GET'])
def get_logs():
    # Returns the logs for your React dashboard polling
    return jsonify(detections)

@app.route('/api/new_detection', methods=['POST'])
def new_detection():
    data = request.json
    # Assign a unique ID for the React list
    data['id'] = len(detections) + 1
    detections.insert(0, data)
    # Keep the feed manageable (last 15 entries)
    if len(detections) > 15:
        detections.pop()
    return jsonify({"status": "success"})

@app.route('/api/enroll', methods=['POST'])
def enroll_user():
    try:
        data = request.json
        person_name = data.get('name', 'new_user') # Name from your React prompt
        print(f"--- Triggering Enrollment for: {person_name} ---")

        # Define full paths to each script
        capture_script = os.path.join(BACKEND_DIR, "capture_face.py")
        extract_script = os.path.join(BACKEND_DIR, "extract_embeddings.py")
        build_script = os.path.join(BACKEND_DIR, "build_index.py")

        # 1. Run Capture (This pops the camera window)
        subprocess.run([PYTHON_EXE, capture_script, person_name], check=True)
        
        # 2. Run Training (Converts photos to data)
        subprocess.run([PYTHON_EXE, extract_script], check=True)
        
        # 3. Run Indexing (Updates the searchable memory)
        subprocess.run([PYTHON_EXE, build_script], check=True)
        
        return jsonify({"status": "success", "message": f"Successfully enrolled {person_name}"})
    except Exception as e:
        print(f"Enrollment Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Start the server on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)