import pickle
import faiss
import numpy as np

# 1. Load your newly created embeddings
with open('embeddings.pkl', 'rb') as f:
    embeddings_db = pickle.load(f)

# 2. Prepare data for FAISS
all_embeddings = []
name_map = []

for name, entries in embeddings_db.items():
    for entry in entries:
        all_embeddings.append(entry['embedding'])
        name_map.append(name)

# Convert to float32 (required by FAISS)
all_embeddings = np.array(all_embeddings).astype('float32')

# 3. Create the FAISS Index (L2 distance is standard)
dimension = 512
index = faiss.IndexFlatL2(dimension)
index.add(all_embeddings)

# 4. Save the index and the name map
faiss.write_index(index, "face_bank.index")
with open("name_map.pkl", "wb") as f:
    pickle.dump(name_map, f)

print("✅ FAISS index 'face_bank.index' created successfully!")