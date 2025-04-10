import pandas as pd
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def embed_question(question, model_name='all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    return model.encode([question])[0]

def search_chunks(query_vec, top_k=5):
    df = pd.read_csv("data/chunks.csv")
    index = faiss.read_index("models/faiss_index.index")
    D, I = index.search(np.array([query_vec]), top_k)
    return df.iloc[I[0]].copy()
