import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_file):
    """Reads full text from PDF stream."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def chunk_text(text, chunk_size=300):
    """Splits long text into smaller chunks (~300 characters)."""
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < chunk_size:
            current += sentence + " "
        else:
            chunks.append(current.strip())
            current = sentence + " "

    if current:
        chunks.append(current.strip())

    return chunks
