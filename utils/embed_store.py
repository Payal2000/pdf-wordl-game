import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Pinecone configuration
pinecone_api_key = os.getenv("PINECONE_API_KEY")
pinecone_env = os.getenv("PINECONE_ENV")
pinecone_index_name = os.getenv("PINECONE_INDEX_NAME")

# Initialize Pinecone client
pc = Pinecone(api_key=pinecone_api_key)

# Create the index if it doesn't exist
if pinecone_index_name not in pc.list_indexes().names():
    pc.create_index(
        name=pinecone_index_name,
        dimension=1536,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=pinecone_env)
    )

# Connect to the Pinecone index
index = pc.Index(pinecone_index_name)

# Embedding model
EMBED_MODEL = "text-embedding-3-small"

def embed_text(text: str) -> list:
    text = text.strip()
    if not text:
        raise ValueError("Cannot embed empty text.")

    response = client.embeddings.create(
        input=text,
        model=EMBED_MODEL
    )
    return response.data[0].embedding

def upsert_chunks(chunks: list[str], namespace: str = "default"):
    vectors = []
    for i, chunk in enumerate(chunks):
        chunk = chunk.strip()
        if not chunk:
            continue  # skip empty chunks
        emb = embed_text(chunk)
        vectors.append({
            "id": f"chunk-{i}",
            "values": emb,
            "metadata": {"text": chunk}
        })
    if vectors:
        index.upsert(vectors=vectors, namespace=namespace)

def query_chunks(query: str, top_k: int = 3, namespace: str = "default"):
    query_emb = embed_text(query)
    results = index.query(
        vector=query_emb,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )
    return [match["metadata"]["text"] for match in results["matches"]]
