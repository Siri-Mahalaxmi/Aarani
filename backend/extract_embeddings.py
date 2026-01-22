import os
import pickle
import cv2
import numpy as np
from insightface.app import FaceAnalysis

# MODIFIED: Default database_path set to '../database' to look outside the backend folder
def extract_face_embeddings(database_path='../database', output_file='embeddings.pkl'):
    """
    Extract face embeddings from images in the database folder.
    """
    
    # Initialize the FaceAnalysis app with buffalo_l model
    print("Loading InsightFace model (buffalo_l)...")
    app = FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=-1, det_size=(640, 640))  # ctx_id=-1 for CPU
    
    # Dictionary to store embeddings
    embeddings_db = {}
    
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    # Check if database folder exists
    if not os.path.exists(database_path):
        print(f"Error: Database folder '{database_path}' not found!")
        print(f"Current working directory: {os.getcwd()}")
        return
    
    # Loop through each person's folder
    for person_name in os.listdir(database_path):
        person_folder = os.path.join(database_path, person_name)
        
        # Skip if not a directory
        if not os.path.isdir(person_folder):
            continue
        
        print(f"\nProcessing folder: {person_name}")
        embeddings_db[person_name] = []
        
        # Loop through all images in the person's folder
        for image_file in os.listdir(person_folder):
            if not image_file.lower().endswith(image_extensions):
                continue
            
            image_path = os.path.join(person_folder, image_file)
            
            try:
                img = cv2.imread(image_path)
                if img is None:
                    print(f"  ⚠ Could not read image: {image_file}")
                    continue
                
                # Detect faces and get embeddings
                faces = app.get(img)
                
                if len(faces) == 0:
                    print(f"  ⚠ No face detected in: {image_file}")
                    continue
                
                # Get the largest face
                face = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
                embedding = face.embedding
                
                # Store the embedding
                embeddings_db[person_name].append({
                    'embedding': embedding,
                    'image_file': image_file
                })
                print(f"  ✓ Extracted embedding from: {image_file}")
                
            except Exception as e:
                print(f"  ✗ Error processing {image_file}: {str(e)}")
                continue
    
    # Save embeddings to pickle file
    if embeddings_db:
        with open(output_file, 'wb') as f:
            pickle.dump(embeddings_db, f)
        
        print(f"\n{'='*60}")
        print(f"SUCCESS! Embeddings saved to '{output_file}'")
        print(f"{'='*60}")
        
        for person, embeddings in embeddings_db.items():
            print(f"  {person}: {len(embeddings)} embeddings")
    else:
        print("\n⚠ No embeddings were extracted.")

if __name__ == "__main__":
    # MODIFIED: Explicitly calling the path outside the current folder
    extract_face_embeddings(database_path='../database', output_file='embeddings.pkl')
    
    print("\n" + "="*60)
    print("You can now use 'embeddings.pkl' for your live hackathon!")
    print("="*60)