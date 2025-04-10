import numpy as np
import faiss

def build_faiss_index(embedding_path="data/embeddings.npy", save_path="models/faiss_index.index"):
    embeddings = np.load(embedding_path)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, save_path)
    print("✅ FAISS index saved.")
