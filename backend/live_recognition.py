import cv2
import faiss
import pickle
import requests
from insightface.app import FaceAnalysis

# Load the models Person 1 built
index = faiss.read_index("face_bank.index")
with open("name_map.pkl", "rb") as f:
    name_map = pickle.load(f)

app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=-1)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    faces = app.get(frame)
    for face in faces:
        feat = face.embedding.reshape(1, -1).astype('float32')
        D, I = index.search(feat, k=1)
        
        # CHANGE: Increased threshold from 0.6 to 1.0 for better matching
        name = name_map[I[0][0]] if D[0][0] < 250.0 else "Unknown"
        status = "authorized" if name != "Unknown" else "unauthorized"
        
        # VISUAL FEEDBACK: Draw a box and name on the camera window
        bbox = face.bbox.astype(int)
        color = (0, 255, 0) if status == "authorized" else (0, 0, 255)
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        cv2.putText(frame, f"{name} ({D[0][0]:.2f})", (bbox[0], bbox[1]-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Send data to your Dashboard
        try:
            requests.post('http://localhost:5000/api/new_detection', 
                          json={"name": name, "status": status, "timestamp": "Now"})
        except: 
            pass

    cv2.imshow('AI Feed', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()