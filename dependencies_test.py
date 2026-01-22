import mediapipe as mp
import onnx
from insightface.app import FaceAnalysis
print("MediaPipe:", mp.__version__)
print("ONNX:", onnx.__version__)
print("InsightFace OK")
print(mp.solutions.face_mesh)