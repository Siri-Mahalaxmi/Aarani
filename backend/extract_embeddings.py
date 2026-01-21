import os
import pickle
import cv2
import numpy as np
from insightface.app import FaceAnalysis

def extract_face_embeddings(database_path='database', output_file='embeddings.pkl'):
    """
    Extract face embeddings from images in the database folder.
    
    Args:
        database_path: Path to the database folder containing subfolders with images
        output_file: Name of the output pickle file to save embeddings
    """
    
    # Initialize the FaceAnalysis app with buffalo_l model
    print("Loading InsightFace model (buffalo_l)...")
    app = FaceAnalysis(name='buffalo_l')
    app.prepare(ctx_id=-1, det_size=(640, 640))  # ctx_id=0 for GPU, -1 for CPU
    
    # Dictionary to store embeddings: {person_name: [embedding1, embedding2, ...]}
    embeddings_db = {}
    
    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')
    
    # Check if database folder exists
    if not os.path.exists(database_path):
        print(f"Error: Database folder '{database_path}' not found!")
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
            # Check if file is an image
            if not image_file.lower().endswith(image_extensions):
                continue
            
            image_path = os.path.join(person_folder, image_file)
            
            try:
                # Read the image
                img = cv2.imread(image_path)
                
                if img is None:
                    print(f"  ⚠ Could not read image: {image_file}")
                    continue
                
                # Detect faces and get embeddings
                # The app.get() function uses RetinaFace for detection and ArcFace for embedding
                faces = app.get(img)
                
                if len(faces) == 0:
                    print(f"  ⚠ No face detected in: {image_file}")
                    continue
                
                if len(faces) > 1:
                    print(f"  ⚠ Multiple faces detected in: {image_file}, using the largest face")
                
                # Get the largest face (by bounding box area)
                face = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
                
                # Extract the 512-D embedding
                embedding = face.embedding
                
                # Verify embedding dimension
                assert embedding.shape[0] == 512, f"Expected 512-D embedding, got {embedding.shape[0]}-D"
                
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
        
        # Print summary
        print("\nSummary:")
        for person, embeddings in embeddings_db.items():
            print(f"  {person}: {len(embeddings)} embeddings")
        
        total_embeddings = sum(len(embs) for embs in embeddings_db.values())
        print(f"\nTotal: {total_embeddings} face embeddings from {len(embeddings_db)} people")
    else:
        print("\n⚠ No embeddings were extracted. Please check your images.")


if __name__ == "__main__":
    # Run the extraction
    extract_face_embeddings(database_path='database', output_file='embeddings.pkl')
    
    print("\n" + "="*60)
    print("You can now use 'embeddings.pkl' for your live hackathon!")
    print("="*60)