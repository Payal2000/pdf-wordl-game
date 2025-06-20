import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_clue(word: str, context_chunks: list[str]) -> str:
    context = "\n".join(context_chunks)

    prompt = f"""
You are a trivia game master. Your job is to write a single, clever, trivia-style clue for a word, using ONLY the text below.

Only use facts and context from this document. Do not add outside information.

---
📘 Document Excerpt:
\"\"\"
{context}
\"\"\"

🎯 Target Word: {word}

Write a trivia clue (1–2 sentences), grounded only in the document text:
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
