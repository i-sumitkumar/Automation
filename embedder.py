import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import os

def embed_chunks(csv_path="data/chunks.csv", model_name="all-MiniLM-L6-v2"):
    model = SentenceTransformer(model_name)
    df = pd.read_csv(csv_path)
    embeddings = model.encode(df['chunk_text'].tolist(), show_progress_bar=True)
    np.save("data/embeddings.npy", embeddings)
    return df, embeddings
