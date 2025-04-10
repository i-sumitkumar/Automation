import fitz
import re
import pandas as pd

def extract_pdf_chunks(pdf_path, chunk_size=300, overlap=50):
    doc = fitz.open(pdf_path)
    chunks, buffer, heading, idx = [], [], "Unknown", 0

    for page_num in range(len(doc)):
        blocks = sorted(doc.load_page(page_num).get_text("blocks"), key=lambda b: b[1])
        for block in blocks:
            text = block[4].strip()
            if not text:
                continue
            if re.match(r"^\d+(\.\d+)*\s+[A-Z]", text):
                heading = text
            words = text.split()
            buffer += words
            if len(buffer) >= chunk_size:
                chunks.append({
                    "chunk_index": idx,
                    "heading": heading,
                    "page_num": page_num + 1,
                    "chunk_text": ' '.join(buffer)
                })
                buffer = buffer[-overlap:]
                idx += 1
    return pd.DataFrame(chunks)
