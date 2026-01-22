import pickle
import numpy as np
import faiss
import os

# File paths (should be in the same directory as this script)
EMBEDDINGS_FILE = "embeddings.pkl"
FAISS_INDEX_FILE = "face_bank.index"
NAME_MAP_FILE = "name_map.pkl"

def rebuild_faiss_index():
    """Rebuild FAISS index with proper normalization"""
    
    print("="*60)
    print("REBUILDING FAISS INDEX WITH NORMALIZATION")
    print("="*60)
    
    # Load embeddings
    print("\n[1/5] Loading embeddings.pkl...")
    try:
        with open(EMBEDDINGS_FILE, 'rb') as f:
            embeddings_db = pickle.load(f)
        print(f"✓ Loaded embeddings for {len(embeddings_db)} people")
    except FileNotFoundError:
        print(f"✗ ERROR: '{EMBEDDINGS_FILE}' not found!")
        print("Please run extract_embeddings.py first.")
        return
    
    # Prepare data
    print("\n[2/5] Extracting embeddings...")
    all_embeddings = []
    name_map = []
    
    for person_name, face_list in embeddings_db.items():
        print(f"  • {person_name}: {len(face_list)} face(s)")
        for face_data in face_list:
            embedding = face_data['embedding']
            all_embeddings.append(embedding)
            name_map.append(person_name)
    
    # Convert to numpy array
    embeddings_array = np.array(all_embeddings).astype('float32')
    print(f"\n✓ Total embeddings: {embeddings_array.shape[0]}")
    print(f"✓ Embedding dimension: {embeddings_array.shape[1]}")
    
    # CRITICAL: Normalize embeddings
    print("\n[3/5] Normalizing embeddings (CRITICAL STEP)...")
    faiss.normalize_L2(embeddings_array)
    print("✓ All embeddings normalized")
    
    # Create FAISS index
    print("\n[4/5] Building FAISS index...")
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)
    print(f"✓ Added {index.ntotal} vectors to index")
    
    # Save files
    print("\n[5/5] Saving files...")
    faiss.write_index(index, FAISS_INDEX_FILE)
    print(f"✓ Saved: {FAISS_INDEX_FILE}")
    
    with open(NAME_MAP_FILE, 'wb') as f:
        pickle.dump(name_map, f)
    print(f"✓ Saved: {NAME_MAP_FILE}")
    
    # Test the index
    print("\n" + "="*60)
    print("TESTING INDEX")
    print("="*60)
    
    test_embedding = embeddings_array[0:1]
    distances, indices = index.search(test_embedding, k=1)
    distance = distances[0][0]
    confidence = 1 - (distance / 2)
    matched_name = name_map[indices[0][0]]
    
    print(f"\nTest search result:")
    print(f"  Distance: {distance:.4f} (should be ~0.0 for same face)")
    print(f"  Confidence: {confidence:.4f} (should be ~1.0 for same face)")
    print(f"  Matched name: {matched_name}")
    
    print("\n" + "="*60)
    print("✓ SUCCESS! Your FAISS index is now ready!")
    print("="*60)
    print("\nNext steps:")
    print("1. Start your FastAPI server: python backend/main.py")
    print("2. Test with: python backend/test_client.py")
    print("="*60)

if __name__ == "__main__":
    rebuild_faiss_index()