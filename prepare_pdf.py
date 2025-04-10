from pdf_chunker import extract_pdf_chunks
from embedder import embed_chunks
from faiss_indexer import build_faiss_index

def prepare(pdf_path):
    df = extract_pdf_chunks(pdf_path)
    df.to_csv("data/chunks.csv", index=False)
    _, embeddings = embed_chunks("data/chunks.csv")
    build_faiss_index("data/embeddings.npy")
    print("✅ PDF processing complete. Ready for retrieval.")