import asyncio
import base64
import json
import pickle
import os
import numpy as np
import cv2
import faiss
import mediapipe as mp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from insightface.app import FaceAnalysis
from concurrent.futures import ThreadPoolExecutor
import uvicorn

# Initialize FastAPI app
app = FastAPI(title="Face Recognition & Liveness Server")

# Global variables
face_app = None
faiss_index = None
name_map = None
executor = ThreadPoolExecutor(max_workers=4)

# MediaPipe Liveness Setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "face_bank.index")
NAME_MAP_PATH = os.path.join(PROJECT_ROOT, "name_map.pkl")
CONFIDENCE_THRESHOLD = 0.4
EAR_THRESHOLD = 0.2  # Threshold for a "closed" eye

# Dictionary to track liveness state per connection
# Key: websocket, Value: {"blink_count": int, "is_live": bool}
liveness_tracker = {}

def calculate_ear(landmarks, eye_indices):
    """Calculate Eye Aspect Ratio (EAR)"""
    # Vertical distances
    v1 = np.linalg.norm(np.array([landmarks[eye_indices[1]].x, landmarks[eye_indices[1]].y]) - 
                        np.array([landmarks[eye_indices[5]].x, landmarks[eye_indices[5]].y]))
    v2 = np.linalg.norm(np.array([landmarks[eye_indices[2]].x, landmarks[eye_indices[2]].y]) - 
                        np.array([landmarks[eye_indices[4]].x, landmarks[eye_indices[4]].y]))
    # Horizontal distance
    h = np.linalg.norm(np.array([landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y]) - 
                       np.array([landmarks[eye_indices[3]].x, landmarks[eye_indices[3]].y]))
    return (v1 + v2) / (2.0 * h)

def load_models():
    global face_app, faiss_index, name_map
    print("Loading Models...")
    face_app = FaceAnalysis(name='buffalo_l')
    face_app.prepare(ctx_id=-1, det_size=(640, 640))
    faiss_index = faiss.read_index(FAISS_INDEX_PATH)
    with open(NAME_MAP_PATH, 'rb') as f:
        data = pickle.load(f)
        name_map = {i: name for i, name in enumerate(data)} if isinstance(data, list) else data
    print("✓ Models & Liveness Ready!")

def process_frame(img_data, websocket_id):
    try:
        img_bytes = base64.b64decode(img_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return {"error": "Decode failed"}

        # 1. Liveness Detection (Blink Check)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mesh_results = face_mesh.process(rgb_img)
        
        is_live = False
        if mesh_results.multi_face_landmarks:
            landmarks = mesh_results.multi_face_landmarks[0].landmark
            # MediaPipe eye indices
            left_ear = calculate_ear(landmarks, [362, 385, 387, 263, 373, 380])
            right_ear = calculate_ear(landmarks, [33, 160, 158, 133, 153, 144])
            avg_ear = (left_ear + right_ear) / 2.0

            # Update tracker
            state = liveness_tracker.get(websocket_id, {"blink_count": 0, "is_live": False})
            if avg_ear < EAR_THRESHOLD:
                state["blink_count"] += 1
            if state["blink_count"] >= 3:
                state["is_live"] = True
            
            liveness_tracker[websocket_id] = state
            is_live = state["is_live"]

        # 2. Face Recognition
        faces = face_app.get(img)
        results = []
        for face in faces:
            embedding = face.embedding.reshape(1, -1).astype('float32')
            faiss.normalize_L2(embedding)
            distances, indices = faiss_index.search(embedding, k=1)
            
            confidence = float(1 - distances[0][0])
            name = name_map.get(indices[0][0], "Unknown") if confidence >= CONFIDENCE_THRESHOLD else "Unknown"
            bbox = face.bbox.astype(int).tolist()

            results.append({
                "name": name,
                "confidence": round(confidence, 3),
                "is_live": is_live, # The critical flag for the win!
                "bbox": {"x1": bbox[0], "y1": bbox[1], "x2": bbox[2], "y2": bbox[3]}
            })
        
        return {"faces": results}
    except Exception as e:
        return {"error": str(e)}

@app.on_event("startup")
async def startup_event():
    load_models()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_id = id(websocket)
    liveness_tracker[ws_id] = {"blink_count": 0, "is_live": False}
    print(f"✓ Client {ws_id} connected")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(executor, process_frame, message["image"], ws_id)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        liveness_tracker.pop(ws_id, None)
        print(f"✗ Client {ws_id} disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



# CODE PERFECT TILL DAY 2 TASK 1 (TEAMMATE 2), TESTING IS DONE
# import asyncio
# import base64
# import json
# import pickle
# import numpy as np
# import cv2
# import os
# import faiss
# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from fastapi.responses import HTMLResponse
# from insightface.app import FaceAnalysis
# from concurrent.futures import ThreadPoolExecutor
# import uvicorn

# # Initialize FastAPI app
# app = FastAPI(title="Face Recognition WebSocket Server")

# # Global variables for model and FAISS index
# face_app = None
# faiss_index = None
# name_map = None
# executor = ThreadPoolExecutor(max_workers=4)

# # Configuration
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))      # backend/
# PROJECT_ROOT = os.path.dirname(BASE_DIR)                   # araniHackathon/

# FAISS_INDEX_PATH = os.path.join(PROJECT_ROOT, "face_bank.index")
# NAME_MAP_PATH = os.path.join(PROJECT_ROOT, "name_map.pkl")

# CONFIDENCE_THRESHOLD = 0.4  # Adjust based on your needs (lower = stricter)


# def load_models():
#     """Load InsightFace model and FAISS index on startup"""
#     global face_app, faiss_index, name_map
    
#     print("Loading InsightFace model (buffalo_l)...")
#     face_app = FaceAnalysis(name='buffalo_l')
#     face_app.prepare(ctx_id=0, det_size=(640, 640))  # ctx_id=-1 for CPU
    
#     print("Loading FAISS index...")
#     faiss_index = faiss.read_index(FAISS_INDEX_PATH)
    
#     print("Loading name map...")
#     with open(NAME_MAP_PATH, 'rb') as f:
#         loaded_data = pickle.load(f)
        
#         # Handle both list and dict formats
#         if isinstance(loaded_data, list):
#             # Convert list to dict: {index: name}
#             name_map = {i: name for i, name in enumerate(loaded_data)}
#             print(f"  Converted list to dict: {len(name_map)} names")
#         elif isinstance(loaded_data, dict):
#             name_map = loaded_data
#             print(f"  Loaded dict: {len(name_map)} names")
#         else:
#             raise ValueError(f"Unexpected name_map type: {type(loaded_data)}")
    
#     print("✓ All models loaded successfully!")


# def process_frame(img_data):
#     """
#     Process a single frame (CPU-intensive operations)
#     This runs in a separate thread to avoid blocking the event loop
#     """
#     try:
#         # Decode base64 image
#         img_bytes = base64.b64decode(img_data)
#         nparr = np.frombuffer(img_bytes, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
#         if img is None:
#             return {"error": "Failed to decode image"}
        
#         # Detect faces and get embeddings
#         faces = face_app.get(img)
        
#         if len(faces) == 0:
#             return {"faces": []}
        
#         results = []
        
#         for face in faces:
#             # Get the 512-D embedding
#             embedding = face.embedding.reshape(1, -1).astype('float32')
            
#             # Normalize embedding (important for cosine similarity)
#             faiss.normalize_L2(embedding)
            
#             # Search FAISS index (k=1 for nearest neighbor)
#             distances, indices = faiss_index.search(embedding, k=1)
            
#             # Get the matched name
#             matched_idx = indices[0][0]
#             distance = distances[0][0]
            
#             # Convert distance to confidence (cosine similarity)
#             # Distance is L2 distance, convert to similarity score
#             confidence = float(1 - distance)  # Higher is better
            
#             # Get name from name_map
#             name = name_map.get(matched_idx, "Unknown")
            
#             # Apply confidence threshold
#             if confidence < CONFIDENCE_THRESHOLD:
#                 name = "Unknown"
            
#             # Get bounding box
#             bbox = face.bbox.astype(int).tolist()  # [x1, y1, x2, y2]
            
#             results.append({
#                 "name": name,
#                 "confidence": round(confidence, 3),
#                 "bbox": {
#                     "x1": bbox[0],
#                     "y1": bbox[1],
#                     "x2": bbox[2],
#                     "y2": bbox[3]
#                 }
#             })
        
#         return {"faces": results}
    
#     except Exception as e:
#         return {"error": str(e)}


# @app.on_event("startup")
# async def startup_event():
#     """Load models when the server starts"""
#     load_models()


# @app.get("/", response_class=HTMLResponse)
# async def get_test_page():
#     """Simple test page for the WebSocket"""
#     return """
#     <!DOCTYPE html>
#     <html>
#     <head>
#         <title>Face Recognition WebSocket Test</title>
#         <style>
#             body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
#             button { padding: 10px 20px; font-size: 16px; margin: 10px 5px; cursor: pointer; }
#             #status { padding: 10px; margin: 10px 0; border-radius: 5px; }
#             .connected { background-color: #d4edda; color: #155724; }
#             .disconnected { background-color: #f8d7da; color: #721c24; }
#             #results { margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 5px; }
#             pre { background: white; padding: 10px; border-radius: 3px; overflow-x: auto; }
#         </style>
#     </head>
#     <body>
#         <h1>🎭 Face Recognition WebSocket Test</h1>
        
#         <div id="status" class="disconnected">Disconnected</div>
        
#         <button onclick="connect()">Connect</button>
#         <button onclick="disconnect()">Disconnect</button>
#         <button onclick="sendTestImage()">Send Test Image</button>
        
#         <div id="results">
#             <h3>Results:</h3>
#             <pre id="output">No results yet...</pre>
#         </div>
        
#         <script>
#             let ws = null;
            
#             function connect() {
#                 ws = new WebSocket('ws://localhost:8000/ws');
                
#                 ws.onopen = function() {
#                     document.getElementById('status').className = 'connected';
#                     document.getElementById('status').textContent = 'Connected';
#                     console.log('WebSocket connected');
#                 };
                
#                 ws.onmessage = function(event) {
#                     const data = JSON.parse(event.data);
#                     document.getElementById('output').textContent = JSON.stringify(data, null, 2);
#                     console.log('Received:', data);
#                 };
                
#                 ws.onerror = function(error) {
#                     console.error('WebSocket error:', error);
#                 };
                
#                 ws.onclose = function() {
#                     document.getElementById('status').className = 'disconnected';
#                     document.getElementById('status').textContent = 'Disconnected';
#                     console.log('WebSocket disconnected');
#                 };
#             }
            
#             function disconnect() {
#                 if (ws) {
#                     ws.close();
#                 }
#             }
            
#             function sendTestImage() {
#                 if (!ws || ws.readyState !== WebSocket.OPEN) {
#                     alert('Please connect first!');
#                     return;
#                 }
                
#                 // You would send actual base64 image data here
#                 alert('In real usage, send base64-encoded image data to the WebSocket');
#             }
#         </script>
#     </body>
#     </html>
#     """


# @app.websocket("/ws")
# async def websocket_endpoint(websocket: WebSocket):
#     """
#     WebSocket endpoint for real-time face recognition
    
#     Expected input: {"image": "base64_encoded_image_string"}
#     Output: {"faces": [{"name": "...", "confidence": 0.xx, "bbox": {...}}, ...]}
#     """
#     await websocket.accept()
#     print("✓ Client connected")
    
#     try:
#         while True:
#             # Receive data from client
#             data = await websocket.receive_text()
            
#             try:
#                 # Parse JSON
#                 message = json.loads(data)
                
#                 if "image" not in message:
#                     await websocket.send_json({"error": "Missing 'image' field"})
#                     continue
                
#                 # Process image in thread pool to avoid blocking
#                 loop = asyncio.get_event_loop()
#                 result = await loop.run_in_executor(
#                     executor, 
#                     process_frame, 
#                     message["image"]
#                 )
                
#                 # Send result back to client
#                 await websocket.send_json(result)
                
#             except json.JSONDecodeError:
#                 await websocket.send_json({"error": "Invalid JSON format"})
#             except Exception as e:
#                 await websocket.send_json({"error": f"Processing error: {str(e)}"})
    
#     except WebSocketDisconnect:
#         print("✗ Client disconnected")
#     except Exception as e:
#         print(f"WebSocket error: {e}")


# @app.get("/health")
# async def health_check():
#     """Health check endpoint"""
#     return {
#         "status": "healthy",
#         "model_loaded": face_app is not None,
#         "faiss_loaded": faiss_index is not None,
#         "name_map_loaded": name_map is not None
#     }


# if __name__ == "__main__":
#     print("Starting Face Recognition WebSocket Server...")
#     print("WebSocket endpoint: ws://localhost:8000/ws")
#     print("Test page: http://localhost:8000")
    
#     uvicorn.run(
#         app, 
#         host="0.0.0.0", 
#         port=8000,
#         log_level="info"
#     )